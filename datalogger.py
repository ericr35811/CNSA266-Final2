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

		self.LOG_DIR = 'static/logs/'
		self.LOG_FORMAT = 'log_%Y%m%d-%H%M%S.csv'
		self.log_file = None
		self.csv = None

		# list of sensors to monitor
		self.sensors = None

		# task queue
		self.q = Queue()

		# handle for SocketIO to send events
		self.socketio = socketio

	def _log(self):
		# send CPU percents if test mode
		if self.connection.test:
			if self.sensors is not None and self.running:
				cpu = cpu_percent(percpu=True)
				data = []
				elapsed = round(time() - self.t0, 2)

				for i, sensor in enumerate(self.sensors):
					data.append({
						'pid': sensor['pid'],
						'val': round(cpu[i], 2),
						'elapsed': elapsed
					})

				self.socketio.emit('send_data', data)
				self._write_log(elapsed, data)
				self.socketio.sleep(self.rate)
			else:
				print('DataLogger: No sensors to read')

		else:
			if self.connection.connected():
				if self.sensors is not None and self.running:
					data = []
					for sensor in self.sensors:
						print('querying', sensor['pid_int'], sensor['name'])

						r = self.connection.obd.query(obd_commands[1][sensor['pid_int']])

						if r.value is not None:
							elapsed = round(r.time - self.t0, 2)

							print('%20s: %s' % (sensor['name'], str(r.value)))

							data.append({
								'pid': sensor['pid'],
								'val': round(r.value.magnitude, 2),
								'elapsed': elapsed
							})
						else:
							# sometimes the value will be None if only one sensor is selected
							# no idea why, should fix
							print('!!', sensor['name'], 'was None!')
							data.append({
								'pid': sensor['pid'],
								'val': None,				# todo: logging randomly stopped when logging from a real car for a few minutes. thread may have crashed when trying to write None to the csv?
								'elapsed': round(time() - self.t0, 2)
							})

					self.socketio.emit('send_data', data)
					self._write_log(elapsed, data)
					self.socketio.sleep(self.rate)
				elif self.sensors is None:
					print('DataLogger: No sensors to read')
			else:
				print('DataLogger: OBD not connected')
				self.stop()

		# prepare to run this again if running is true
		if self.running:
			self.q.put(self._log)

	def _new_log(self):
		# open a new log file
		# the file handle remains open until logging stops (see _close_log())
		filename = self.LOG_DIR + datetime.now().strftime(self.LOG_FORMAT)
		self.log_file = open(filename, 'w', newline='')
		self.csv = csv.writer(self.log_file)

		# self.socketio.emit('new_log', filename)

		# write the header line (time, pid1, pid2, pid3, etc.)
		self.csv.writerow(['TIME'] + [
			# sets the sensor name and units as the column name
			f'{s["name"]} ({obdsensors.pids[s["pid_int"]][obdsensors.UNIT]})' for s in self.sensors
		])

	def _write_log(self, time, data):
		self.csv.writerow([time] + [
			sensor['val'] for sensor in data
		])

	def _close_log(self):
		self.log_file.close()

	def _start(self):
		if not self.running:
			self._new_log()
			self.t0 = time()
			self.running = True
			self._log()
		else:
			print('DataLogger._start: already running')

	def _stop(self):
		if self.running:
			self._close_log()
			self.running = False
		else:
			print('DataLogger._stop: already stopped')

	def start(self):
		self.q.put(self._start)

	def stop(self):
		self.q.put(self._stop)

	def exit(self):
		self.stop()
		self.q.put(None)

	# main loop of the thread
	def thread(self):
		while True:
			task = self.q.get()

			if task is None:
				break
			else:
				task()
