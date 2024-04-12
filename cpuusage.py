from datetime import datetime
from psutil import cpu_percent


class CpuUsage():
	def __init__(self, socketio):
		self.log = []
		self.running = False
		self.t0 = datetime.now()
		self.interval = 1
		self.socketio = socketio

	def setInterval(self, ms):
		self.interval = ms / 1000

	def addToLog(self):
		elapsed = str((datetime.now() - self.t0))[2:-4]
		percent = str(round(cpu_percent(), 1))
		#self.log.append({'elapsed': elapsed, 'percent': percent})
		self.socketio.emit('sendcpu', {'elapsed': elapsed, 'percent': percent})

	def popFromLog(self):
		return self.log.pop(0)

	def start(self):
		self.t0 = datetime.now()
		self.running = True
		while self.running:
			self.addToLog()
			self.socketio.sleep(self.interval)

	def stop(self):
		self.running = False