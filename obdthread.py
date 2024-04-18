import obd.utils
from obd import OBD, OBDCommand, OBDStatus, OBDResponse, commands as obd_commands

from flask_socketio import SocketIO
from flask import render_template
from threading import Event
from time import time
from queue import Queue


class OBDReader:
	def __init__(self, socketio: SocketIO):
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

	def disconnect(self):
		self.ev.set()
		self.action = 'car_disconnect'

	def get_sensors(self):
		sensorlist = [
			{
				'pid': command.pid,
				'pidhex': f"{command.pid:#04X}",
				'name': command.name,
				'desc': command.desc
			}
			# should check for PIDs that are actually sensors?
			for command in self.connection.supported_commands if
			command.pid is not None and command.command[:2] == b'01'
		]

		sensorlist.sort(key=lambda x: x['pid'])

		return sensorlist

	def _connect(self):
		# waits until connecting is done
		self.connection = OBD(baudrate=9600, portstr='COM3', timeout=1)
		if self.connection.status() == OBDStatus.CAR_CONNECTED:
			print('Connected to car')
			self.socketio.emit('car_connect_status', {'status': True})
		else:
			print('Not connected:', self.connection.status())
			self.socketio.emit('car_connect_status', {'status': False, 'msg': self.connection.status()})

	def _disconnect(self):
		self.connection.close()

	def _log(self):
		if self.connection.status() == OBDStatus.CAR_CONNECTED:

			data = self._get_data()

			self.socketio.emit('sendcpu', data)
			self.socketio.sleep(self.rate)
		else:
			print('thread(): OBD not connected')
			self.socketio.emit('car_connect_status', {'status': False, 'msg': self.connection.status()})
			self.stop()


	def _get_data(self):
		elapsed = time() - self.t0

	def thread(self):
		while True:
			self.ev.wait()

			if self.action == 'car_connect':
				print('car_connect')
				self.ev.clear()
				self._connect()

			elif self.action == 'car_disconnect':
				print('car_disconnect')
				self.ev.clear()
				self._disconnect()

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
				self.action = 'log_run'








