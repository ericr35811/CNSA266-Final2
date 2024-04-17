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
					'pid': command.pid,
					'name': command.name,
					'desc': command.desc
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

	def get_sensors(self):
		self.ev.set()
		self.action = 'get_sensors'

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
		if self.connection.status() == OBDStatus.CAR_CONNECTED:

			data = self._get_data()

			self.socketio.emit('sendcpu', data)
			self.socketio.sleep(self.rate)
		else:
			print('thread(): OBD not connected')
			self.socketio.emit('car_connect_status', {'status': False, 'msg': self.connection.status()})
			self.stop()


	def _get_sensors(self):
		sensors = []
		if self.connection.status() == OBDStatus.CAR_CONNECTED:
			# ask the car for a list of sensors it supports
			r = self.connection.query(obd_commands.PIDS_A)

			print('-- PIDS_A --')
			print(str(r.command))
			print(str(r.value))
			print(str(r.time))
			for message in r.messages:
				print(str(message.data))
				print(str(message.ecu))
				print(str(message.frames))

			# the list of supported PIDs is a bit array, starting at 0x01
			for i, bit in enumerate(r.value, 1):
				# mode 1, pid i
				cmd = obd_commands[1][i]
				if bit:
					self.sensors.add(cmd)
					print(f"""{hex(cmd.pid)}{cmd.name:<20}{cmd.desc}""")



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
			elif self.action == 'get_sensors':
				print('get_sensors')
				self.ev.clear()
				self._get_sensors()








