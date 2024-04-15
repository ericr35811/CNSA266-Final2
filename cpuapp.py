from flask import Flask, render_template, request, session, Response
from socket import gethostname
from flask_socketio import SocketIO, emit
from cpuusage import CpuUsage

# import obd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'RAAAH SECRET'

socketio = SocketIO(app, logger=app.logger, engineio_logger=app.logger)

#app.secret_key = 'supersecret'


class AppState:
	def __init__(self):
		self.connected = False
		self.socketconnected = False


cpulog = CpuUsage(socketio)
appstate = AppState()

socketio.start_background_task(cpulog.loggingThread)


@app.route('/')
def index():
	if not (cpulog.running or appstate.connected):
		appstate.connected = True
		print('user connected')
		return render_template('cputest.html')
	else:
		print('user already connected')
		return 'too many connections'


# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(response):
	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	response.headers['Cache-Control'] = 'public, max-age=0'
	return response


@socketio.on('connect')
def onconnect():
	if not appstate.socketconnected:
		appstate.socketconnected = True
		print('socket connected')
	else:
		print('socket already connected')


@socketio.on('disconnect')
def ondisconnect():
	if appstate.socketconnected:
		appstate.connected = False
		appstate.socketconnected = False
		cpulog.stop()
		print('socket and user disconnected')
	else:
		print('socket and user already disconnected')


@socketio.on('startcpu')
def startcpu():
	if appstate.socketconnected and not cpulog.running:
		print('starting logging')
		appstate.logging = True
		# socketio.start_background_task(cpulog.start)
		# is_logging.set()
		cpulog.start()
	elif not appstate.socketconnected:
		print('socket not connected')
	elif cpulog.running:
		print('logging already running')

	return


@socketio.on('setInterval')
def onSetInterval(interval):
	if appstate.connected:
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
	app.logger.setLevel('DEBUG')
	socketio.run(app, host=ip, allow_unsafe_werkzeug=True)
