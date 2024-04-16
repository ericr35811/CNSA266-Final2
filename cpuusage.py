from datetime import datetime
from psutil import cpu_percent
from threading import Event

class CpuUsage:
	def __init__(self, socketio):
		self.log = []
		self.running = False
		self.t0 = datetime.now()
		self.interval = 1
		self.socketio = socketio
		self.is_logging = Event()

	def setInterval(self, ms):
		self.interval = ms / 1000

	# this function gets run as a separate thread
	def loggingThread(self):
		while True:
			self.is_logging.wait()
			t0 = datetime.now()
			while self.is_logging.is_set():
				elapsed = str((datetime.now() - t0))[2:-4]
				percent = str(round(cpu_percent(), 1))
				self.socketio.emit('sendcpu', {'elapsed': elapsed, 'percent': percent})
				self.socketio.sleep(self.interval)

	def start(self):
		self.t0 = datetime.now()
		self.running = True
		self.is_logging.set()

	def stop(self):
		self.running = False
		self.is_logging.clear()