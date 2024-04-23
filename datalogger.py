from queue import Queue
from time import time
from datetime import datetime
from flask_socketio import SocketIO
from psutil import cpu_percent

import obdsensors
from obd import commands as obd_commands
from carconnection import CarConnection
import csv


class DataLogger:
	def __init__(self, connection: CarConnection, socketio: SocketIO):
		# handle for the OBD connection
		self.connection = connection

		# logging options
		self.rate = 2 # seconds
		self.t0 = None
		self.running = False

		self.LOG_DIR = 'logs/'
		self.LOG_FORMAT = 'log_%Y%m%d-%H%M%S.csv'
		self.log_file = None
		self.csv = None

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
				data = []
				elapsed = round(time() - self.t0, 2)
				# ---- test
				for i, sensor in enumerate(self.sensors):
					data.append({
						'pid': sensor['pid'],
						'val': round(cpu[i], 2),
						'elapsed': elapsed
					})

				# self.socketio.sleep(0.25)
				# ---------

				self.socketio.emit('send_data', data)

				self.csv.writerow([elapsed] + [
					sensor['val'] for sensor in data
				])

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
			# open a new log file
			self.log_file = open(self.LOG_DIR + datetime.now().strftime(self.LOG_FORMAT), 'w', newline='')
			self.csv = csv.writer(self.log_file)

			# write the header line (time, pid1, pid2, pid3, etc.
			self.csv.writerow(['time'] + [
				# sets the sensor name and units as the column name
				f'{s["name"]} ({obdsensors.pids[s["pid_int"]][obdsensors.UNIT]})' for s in self.sensors
			])

			self.running = True
			self.t0 = time()
			self._log()
		else:
			print('DataLogger._start: already running')

		self._f_start = False

	def _stop(self):
		if self.running:
			self.log_file.close()

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
