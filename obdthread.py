from obd import OBD, OBDCommand, OBDStatus, OBDResponse, commands as obd_commands

from flask_socketio import SocketIO
from threading import Event
from time import time
from queue import Queue

class OBDReader:
	class Sensors:
		list = []

		def get_dict(self):
			return [
				{
					'pid': command.name,
					'desc': command.desc,
				}
				for command in self.list
			]

		def clear(self):
			self.list = []

		def add(self, command: OBDCommand):
			self.list.append(command)
			pass

	def __init__(self, socketio: SocketIO):
		self.sensors = self.Sensors()
		self.connection: OBD = None
		# self.sensorlist = []
		self.rate = 1 # seconds
		self.t0 = None

		self.running = False
		self.ev = Event()
		self.action = ''

		self.socketio = socketio

	def start(self):
		self.running = True
		self.ev.set()
		self.action = 'log_start'

	def stop(self):

		self.running = False
		self.ev.set()
		self.action = 'log_stop'

	def connect(self):

		self.ev.set()
		self.action = 'car_connect'

	def _connect(self):
		# waits until connecting is done
		self.connection = OBD()
		if self.connection.status() == OBDStatus.CAR_CONNECTED:
			print('Connected to car')
			self.socketio.emit('car_connect_status', {'status': True})
		else:
			print('Not connected:', self.connection.status())
			self.socketio.emit('car_connect_status', {'status': False, 'msg': self.connection.status()})

	def _log(self):
		if self.connection.status == OBDStatus.CAR_CONNECTED:

			data = self._get_data()

			self.socketio.emit('sendcpu', data)
			self.socketio.sleep(self.rate)
		else:
			print('thread(): OBD not connected')
			self.socketio.emit('car_connect_status', {'status': False, 'msg': self.connection.status()})
			self.stop()


	def _get_sensors(self):
		response = self.connection.query(obd_commands.PIDS_A)

	def _get_data(self):
		elapsed = time() - self.t0

	def thread(self):
		while True:
			self.ev.wait()

			if self.action == 'car_connect':
				print('car_connect')
				self.ev.clear()
				self._connect()
			elif self.action == 'log_start':
				print('log_start')
				self.t0 = time()
				self.ev.set()
				self.action = 'log_run'
			elif self.action == 'log_stop':
				print('log_stop')
				self.ev.clear()
			elif self.action == 'log_run':
				print('log_run')
				self._log()








