from obd import OBD, OBDCommand, OBDStatus, OBDResponse, commands as obd_commands

from flask_socketio import SocketIO
from threading import Event
from time import time


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
		self.ev_running = Event()

		self.socketio = socketio

	def start(self):
		self.running = True
		self.ev_running.set()

	def stop(self):
		self.running = False
		self.ev_running.clear()

	def connect(self,):
		self.connection = OBD()

	def _get_sensors(self):
		response = self.connection.query(obd_commands.PIDS_A)

	def _get_data(self):
		elapsed = time() - self.t0

	def thread(self):
		if self.connection is not None and self.connection.status() == OBDStatus.CAR_CONNECTED:
			while True:
				self.ev_running.wait()

				self.t0 = time()
				while self.ev_running.is_set():
					data = self._get_data()

					self.socketio.emit('sendcpu', data)
					self.socketio.sleep(self.rate)
		else:
			raise Exception('OBDReader.thread(): Cannot start because OBD connection is down')



