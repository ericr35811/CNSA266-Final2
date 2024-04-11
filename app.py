from flask import Flask, render_template, request, session, Response
from psutil import cpu_percent
from datetime import datetime
from socket import gethostname
from flask_socketio import SocketIO, emit
from enum import Enum
# import obd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'RAAAH SECRET'

socketio = SocketIO(app)


#app.secret_key = 'supersecret'


# @app.route('/cpu', methods=['GET', 'POST'])
# def index():
# 	if request.method == 'POST':
# 		elapsed = str((datetime.now() - session['t0']))[2:-4]
# 		percent = str(round(cpu_percent(), 1))
# 		print(percent)
# 		return elapsed + '|' + percent
# 	else:
# 		session['t0'] = datetime.now()
# 		return render_template('main.html')


class CpuUsage:
	def __init__(self):
		self.log = []
		self.running = False
		self.t0 = datetime.now()
		self.interval = 1

	def setInterval(self, ms):
		self.interval = ms / 1000

	def addToLog(self):
		elapsed = str((datetime.now() - self.t0))[2:-4]
		percent = str(round(cpu_percent(), 1))
		#self.log.append({'elapsed': elapsed, 'percent': percent})
		socketio.emit('sendcpu', {'elapsed': elapsed, 'percent': percent})

	def popFromLog(self):
		return self.log.pop(0)

	def start(self):
		self.running = True
		while self.running:
			self.addToLog()
			socketio.sleep(self.interval)

	def stop(self):
		self.running = False

class AppState:
	def __init__(self):
		self.connected = False


cpulog = CpuUsage()
appstate = AppState()

@app.route('/')
def index():
	if not appstate.connected:
		appstate.connected = True
		return render_template('main.html')
	else:
		return 'too many connections'

@socketio.on('connect')
def onconnect():
	print('connected')

@socketio.on('disconnect')
def ondisconnect():
	appstate.connected = False
	cpulog.stop()
	print('disconnected')


@socketio.on('startcpu')
def startcpu():
	socketio.start_background_task(cpulog.start())
	return

@socketio.on('getcpu')
def getcpu():
	data = cpulog.popFromLog()
	emit('sendcpu', data)

@socketio.on('setInterval')
def onSetInterval(interval):
	cpulog.setInterval(interval)

# STATIC ASSETS, MOVE THESE -------------------------------
@app.route('/js/<filename>')
def js(filename):
	with open('js/' + filename) as f:
		return Response(f.read(), mimetype='text/javascript')




if __name__ == '__main__':
	#app.run(debug=True)

	if gethostname() == 'raspberrypi':
		ip = '100.103.188.37'
	else:
		ip = '127.0.0.1'

	#app.run(host=ip)

	socketio.run(app, host=ip)
