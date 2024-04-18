import obd.utils
from obd import OBD, OBDCommand, OBDStatus, OBDResponse, commands as obd_commands

from flask_socketio import SocketIO
from flask import render_template
from threading import Event
from time import time
from queue import Queue


class CarConnection:
	def __init__(self, socketio):
		self.connection: OBD = None

		self.running = False
		self.ev = Event()
		self.action = ''

		self.socketio = socketio

	def _connect(self):
		# waits until connecting is done
		#self.connection = OBD(baudrate=9600, portstr='COM3', timeout=1)
		self.connection = OBD()
		if self.connected():
			print('Connected to car')
			self.socketio.emit('car_connect_status', {'status': True})
		else:
			print('Not connected:', self.connection.status())
			self.socketio.emit('car_connect_status', {'status': False, 'msg': self.connection.status()})

	def _disconnect(self):
		if self.connection is not None:
			self.connection.close()

	def connected(self):
		return self.connection is not None and self.connection.status() == OBDStatus.CAR_CONNECTED

	# does not need to be threaded, none of this should block
	def get_sensors(self):
		if self.connected():
			# create an array of dicts for each PID, to pass to the sensorlist.html template
			sensorlist = [
				{
					'pid': command.pid,
					'pidhex': f"{command.pid:#04X}",
					'name': command.name,
					'desc': command.desc
				}
				# should check for PIDs that are actually sensors?
				for command in self.connection.supported_commands
					# only include if the command has a PID and belongs to mode 1
					if command.pid is not None and command.command[:2] == b'01'
			]

			# supported_commands is unordered, so sort the new list by PID
			sensorlist.sort(key=lambda x: x['pid'])

			return sensorlist

	def connect(self):
		self.ev.set()
		self.action = 'car_connect'

	def disconnect(self):
		self.ev.set()
		self.action = 'car_disconnect'

	def connmon_thread(self):
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


class DataLogger:
	def __init__(self, car_connection: CarConnection, socketio: SocketIO):
		self.car_connection = car_connection
		# self.sensorlist = []
		self.rate = 1 # seconds
		self.t0 = None

		self.running = False
		self.ev = Event()

		self.socketio = socketio

	def start(self):
		self.running = True
		self.ev.set()

	def stop(self):
		self.running = False
		self.ev.clear()

	def _log(self):
		if self.car_connection.connected():
			data = self._get_data()

			self.socketio.emit('sendcpu', data)
			self.socketio.sleep(self.rate)
		else:
			print('thread(): OBD not connected')
			self.socketio.emit('car_connect_status', {'status': False, 'msg': self.car_connection.connection.status()})
			self.stop()

	def _get_data(self):
		elapsed = time() - self.t0

	def log_thread(self):
		while True:
			self.ev.wait()

			while self.ev.is_set():
				self._log()


