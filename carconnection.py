from obd import OBD, OBDStatus, commands as obd_commands
from queue import Queue
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
		# flags to prevent loads of duplicate events on the queue
		self._f_connect = False
		self._f_disconnect = False
		self._f_check_status = False

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

		if self._f_connect:
			self._f_connect = False

	# close the OBD connection
	def _disconnect(self):
		if self.obd is not None:
			self.obd.close()

		self.q.put(self._check_status)

		if self._f_disconnect:
			self._f_disconnect = False

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

		if self._f_check_status:
			self._f_check_status = False

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

	def check_status(self, force=False):
		if not self._f_check_status:
			self._f_check_status = True
			self.q.put(lambda: self._check_status(force))

	def exit(self):
		self.disconnect()
		self.q.put(None)

	# main loop
	def thread(self):
		self.q.put(self._check_status)

		while True:
			# wait for a task on the queue
			task = self.q.get()
			if task is None:
				break
			else:
				task()


