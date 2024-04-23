import obd.utils
from obd import OBD, OBDCommand, OBDStatus, OBDResponse, commands as obd_commands

from flask_socketio import SocketIO
from threading import Event, Thread
from queue import Queue
from psutil import cpu_percent
from time import time
import obdsensors

class CarConnection:
	def __init__(self, socketio, test=False):
		# OBD connection object
		self.obd: OBD = None

		# misc connection options
		self.test = test
		self.BAUD = None
		self.PORT = None

		# options
		self.rate = 0.5

		# connection status
		# only for _check_status()
		self.status = False

		# list of supported sensors
		self.sensors = []

		# task queue
		self.q = Queue()
		self.tasks = []
		# flags to prevent loads of duplicate events on the queue
		self._f_connect = False
		self._f_disconnect = False

		# SocketIO connection for sending events
		self.socketio = socketio

	# check if OBD is connected
	def connected(self):
		return self.obd is not None and self.obd.status() == OBDStatus.CAR_CONNECTED

	# create the OBD connection
	def _connect(self):
		if not self.connected():
			# waits until connecting is done
			self.obd = OBD(baudrate=self.BAUD, portstr=self.PORT)
			if self.connected():
				print('CarConnection: Connected to car')
				self._get_sensors()
				self._check_status(force=True)
			else:
				print('CarConnection: Not connected:', self.obd.status())
				if self.test:
					self._get_sensors()
					self._check_status(force=True)
		else:
			print('CarConnection: Already connected')

		self._f_connect = False

	# close the OBD connection
	def _disconnect(self):
		if self.obd is not None:
			self.obd.close()

		self._f_disconnect = False
		self.q.put(self._check_status)

	# check whether the connection status has changed, and send an event to the client if it has
	def _check_status(self, force=False):
		s = self.connected()

		if s != self.status or force:
			self.status = s
			# wait for browser to acknowledge the event
			self.socketio.emit('car_connect_status', s)

		self.socketio.sleep(self.rate)

		# prepare to run this again
		self.q.put(self._check_status)

	# prepare the list of supported sensors and information about each one
	def _get_sensors(self):
		supported = self.obd.supported_commands

		# override supported if testing
		if self.test:
			supported = {
				cmd for cmd in obd_commands[1][4:12]
			}

		# create an array of dicts for each PID, to pass to the sensorlist.html template
		self.sensors = [
			{
				'pid': f"0x{command.pid:02X}", # format as hexadecimal
				'pid_int': command.pid,
				'name': command.name,
				'desc': command.desc,
				'min': obdsensors.pids[command.pid][obdsensors.MIN],
				'max': obdsensors.pids[command.pid][obdsensors.MAX],
				'unit': obdsensors.pids[command.pid][obdsensors.UNIT]
			}
			for command in supported
				# only include if the command has a live data PID and belongs to mode 1 (live data)
				if command.pid in obdsensors.pids.keys() and command.command[:2] == b'01'
		]

		# supported_commands is unordered, so sort the new list by PID
		self.sensors.sort(key=lambda x: x['pid'])

	# ----- task creators ------
	def connect(self):
		if not self._f_connect:
			self._f_connect = True
			self.q.put(self._connect)

	def disconnect(self):
		if not self._f_disconnect:
			self._f_disconnect = True
			self.q.put(self._disconnect)

	def exit(self):
		self.disconnect()
		self.q.put(None)

	# main loop
	def thread(self):
		while True:
			# wait for a task on the queue
			task = self.q.get()
			if task is None:
				break
			else:
				task()


class DataLogger:
	def __init__(self, connection: CarConnection, socketio: SocketIO):
		# handle for the OBD connection
		self.connection = connection

		# logging options
		self.rate = 2 # seconds
		self.t0 = None
		self.running = False

		# list of sensors to monitor
		self.sensors = None

		# task queue
		self.q = Queue()
		self._f_start = False
		self._f_stop = False

		# handle for SocketIO to send events
		self.socketio = socketio

	# def set_sensors(self, sensors):
	# 	self.sensors = sensors

	def _log(self):
		if self.connection.test:
			if self.sensors is not None:
				cpu = cpu_percent(percpu=True)
				data = [
					{
						'pid': sensor['pid'],
						'val': round(cpu[i], 2),
						'elapsed': round(time() - self.t0, 2)
					}
					for i, sensor in enumerate(self.sensors)
				]

				self.socketio.emit('send_data', data)
				self.socketio.sleep(self.rate)
			else:
				print('DataLogger: No sensors to read')

		else:
			if self.connection.connected():
				if self.sensors is not None:
					data = []
					# ---- test
					for sensor in self.sensors:
						print('querying', sensor['pid_int'], sensor['name'])
						r = self.connection.obd.query(obd_commands[1][sensor['pid_int']])
						print('%20s: %s' % (sensor['name'], str(r.value)))
						if r.value is not None:
							data.append({
								'pid': sensor['pid'],
								'val': round(r.value.magnitude, 2),
								'elapsed': round(time() - self.t0, 2)
							})
						else:
							print('!!', sensor['name'], 'was None!')
							data.append({
								'pid': sensor['pid'],
								'val': None,
								'elapsed': round(time() - self.t0, 2)
							})

						#self.socketio.sleep(0.25)
					# ---------

					self.socketio.emit('send_data', data)
					self.socketio.sleep(self.rate)
				else:
					print('DataLogger: No sensors to read')
			else:
				print('DataLogger: OBD not connected')
				self.stop()

		# prepare to run this again if running is true
		if self.running:
			self.q.put(self._log)

	def _start(self):
		if not self.running:
			self.running = True
			self.t0 = time()
			self._log()
		else:
			print('DataLogger._start: already running')

		self._f_start = False

	def _stop(self):
		if self.running:
			self.running = False
		else:
			print('DataLogger._stop: already stopped')

		self._f_stop = False

	def start(self):
		if not self._f_start:
			self._f_start = True
			self.q.put(self._start)

	def stop(self):
		if not self._f_stop:
			self._f_stop = True
			self.q.put(self._stop)

	def exit(self):
		self.stop()
		self.q.put(None)

	def thread(self):
		while True:
			task = self.q.get()

			# print('*', task.__name__)
			# for x in self.q.queue:
			# 	print(x.__name__)

			if task is None:
				break
			else:
				task()


