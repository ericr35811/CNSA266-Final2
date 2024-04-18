import obd.utils
from obd import OBD, OBDCommand, OBDStatus, OBDResponse, commands as obd_commands

from flask_socketio import SocketIO
from threading import Event, Thread
from psutil import cpu_percent
from time import time


def close_threads(threads):
	for thread in threads:
		print('Stopping', thread[1].name, end='...')
		# call the cleanup function
		thread[0]()
		# wait for the thread to finish
		if thread[1]: thread[1].join()
		print('stopped')


class CarConnection:
	def __init__(self, socketio, test=False):
		self.obd: OBD = None

		self.test = test

		self.running = False
		self.ev = Event()
		self.action = ''

		self.socketio = socketio

		self.rate = 0.5
		self.status = None
		self.sensors = []

	def _connect(self):
		self.status = None
		# waits until connecting is done
		#self.connection = OBD(baudrate=9600, portstr='COM3', timeout=1)
		self.obd = OBD()
		if self.connected():
			print('CarConnection: Connected to car')
			self._get_sensors()
		else:
			print('CarConnection: Not connected:', self.obd.status())
			if self.test:
				self._get_sensors()

	def _disconnect(self):
		if self.obd is not None:
			self.obd.close()

	def _check_status(self):
		s = self.connected()
		# send an event if the state of the connection has changed
		if s != self.status:
			self.status = s
			# wait for browser to acknowledge the event
			self.socketio.emit('car_connect_status', s)

		self.socketio.sleep(self.rate)

	def connected(self):
		return self.obd is not None and self.obd.status() == OBDStatus.CAR_CONNECTED

	# does not need to be threaded, none of this should block
	def _get_sensors(self):
		supported = self.obd.supported_commands

		if self.test:
			supported = {
				obd_commands.ENGINE_LOAD,
				obd_commands.COOLANT_TEMP,
				obd_commands.INTAKE_PRESSURE,
				obd_commands.RPM
			}

		# create an array of dicts for each PID, to pass to the sensorlist.html template
		self.sensors = [
			{
				'pid': f"0x{command.pid:02X}", # format as hexadecimal
				'name': command.name,
				'desc': command.desc
			}
			# should check for PIDs that are actually sensors?
			for command in supported
				# only include if the command has a PID and belongs to mode 1 (live data)
				if command.pid is not None and command.command[:2] == b'01'
		]

		# supported_commands is unordered, so sort the new list by PID
		self.sensors.sort(key=lambda x: x['pid'])

	def connect(self):
		self.action = 'car_connect'
		self.ev.set()


	def disconnect(self):
		self.action = 'car_disconnect'
		self.ev.set()

	def connmon_thread(self):
		while True:
			if self.ev.is_set():
				if self.action == 'car_connect':
					print('CarConnection: car_connect')
					self.ev.clear()
					self.action = ''
					self._connect()

				elif self.action == 'car_disconnect':
					print('CarConnection: car_disconnect')
					self.ev.clear()
					self.action = ''
					self._disconnect()

				elif self.action == 'app_exit':
					self.ev.clear()
					break
			else:
				self.action = 'monitor'
				self._check_status()

	def app_exit(self):
		self.disconnect()
		self.action = 'app_exit'
		self.ev.set()


class DataLogger:
	def __init__(self, connection: CarConnection, socketio: SocketIO):
		self.connection = connection
		self.rate = 0.5 # seconds
		self.t0 = None
		self.sensors = None

		self.running = False
		self.ev = Event()
		self.action = ''

		self.socketio = socketio

	def start(self):
		self.running = True
		self.t0 = time()
		self.ev.set()

	def stop(self):
		self.running = False
		self.ev.clear()

	def set_sensors(self, sensors):
		self.sensors = sensors

	def _log(self):
		# stopped here
		if self.connection.connected() or self.connection.test:
			if self.sensors is not None:
				data = [
					{
						'pid': sensor['pid'],
						'val': round(cpu_percent(), 2),
						'elapsed': round(time() - self.t0, 2)
					}
					for sensor in self.sensors
				]

				self.socketio.emit('send_data', data)
				self.socketio.sleep(self.rate)
			else:
				print('DataLogger: No sensors to read')
		else:
			print('DataLogger: OBD not connected')
			self.stop()

	def log_thread(self):
		while True:
			self.ev.wait()

			if self.action == 'app_exit':
				self.ev.clear()
				break

			while self.ev.is_set():
				self._log()

	def app_exit(self):
		self.stop()
		self.action = 'app_exit'
		self.ev.set()

