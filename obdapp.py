from flask import Flask, render_template, request
from socket import gethostname
from flask_socketio import SocketIO
from carconnection import CarConnection
from datalogger import DataLogger
from atexit import register as atexit_register
from signal import signal, SIGINT
from werkzeug.serving import ThreadedWSGIServer
from time import sleep
from sys import exit, argv
from os import urandom, path
from glob import glob

TEST = False

for arg in argv[1:]:
	if arg == '--test':
		TEST = True

if gethostname() == 'raspberrypi':
	if TEST:
		# use tailscale ip if testing
		ip = '100.103.188.37'
	else:
		# use hotspot ip
		ip = '10.42.0.1'
else:
	# use localhost if not running on the pi
	ip = '127.0.0.1'


# create the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(24)

# create the SocketIO app based on the Flask app
socketio = SocketIO(app, async_mode='threading',logger=app.logger, engineio_logger=app.logger)

# instantiate classes for background tasks
# CarConnection monitors the OBD connection, and DataLogger reads data from the car
# These are background tasks because they would freeze the web server
# the threads are controlled via the classes
obd = CarConnection(socketio, test=TEST)
data_logger = DataLogger(obd, socketio)

# FLASK ROUTES -------------------------------------------------------------------------

# main page
@app.route('/')
def index():
	return render_template('main.html')


# return HTML for the sensor selection card
# gets inserted into main.html with jQuery
@app.route('/templates/card/selectsensors.html')
def menu_selectsensors():
	return render_template('menu/selectsensors.html', sensors=obd.sensors)


# URL for the sensor selection page to POST to
@app.route('/forms/selectsensors', methods=['POST'])
def form_selectsensors():
	if request.method == 'POST':
		# list of PIDs representing each checked sensor
		selected = request.form.getlist('chkSensors')
		# get sensors info by PID
		sensors = [s for s in obd.sensors if s['pid'] in selected]
		# data_logger.set_sensors(sensors)
		data_logger.sensors = sensors

		# returns HTML for the logging card
		# gets inserted into main.html with jQuery
		return render_template('card/logging.html', sensors=sensors)


# returns HTML for the log file selection menu
# gets inserted with jQuery
@app.route('/templates/menu/logfiles.html')
def menu_logfiles():
	# logfiles = listdir(data_logger.LOG_DIR)
	logfiles = [path.basename(p) for p in glob(data_logger.LOG_DIR + '*.csv')]
	logfiles.sort()
	return render_template('menu/logfiles.html', logfiles=logfiles, path=data_logger.LOG_DIR)

# disables client-side caching
# not sure if necessary
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(response):
	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	response.headers['Cache-Control'] = 'public, max-age=0'
	return response

# SOCKETIO EVENT HANDLERS ---------------------------------------------


# fires when a client connects to SocketIO
@socketio.on('connect')
def onconnect():
	print('socketio client connected')
	# if the user reloads the page or connects for the first time, send them the connection status
	# socketio.emit('car_connect_status', obd.status)
	#obd.check_status(force=True)
	obd.send_status()


# fires when a client disconnects from SocketIO
@socketio.on('disconnect')
def ondisconnect():
	print('socketio client disconnected')
	data_logger.stop()


# fires when the "Connect to car" button is pressed
@socketio.on('car_connect')
def car_connect():
	print('Connecting to car')
	obd.connect()
	return True


# fires when the "Disconnect" button is pressed
@socketio.on('car_disconnect')
def car_disconnect():
	print('Disconnecting from car')
	obd.disconnect()


# fires when the "Start" button is pressed on the logging card
@socketio.on('log_start')
def start_logging():
	data_logger.start()


# fires when the "Stop" button is pressed on the logging card
@socketio.on('log_stop')
def stop_logging():
	data_logger.stop()


# fires when the polling rate is changed on the logging card
@socketio.on('log_rate')
def log_rate(rate):
	data_logger.rate = float(rate)


if __name__ == '__main__':
	app.logger.setLevel('DEBUG')

	wsgi_server = ThreadedWSGIServer(app=app, host=ip, port=5000)

	# create processes as SocketIO background tasks (threads)
	print('starting server thread', end='...')
	t_server = socketio.start_background_task(wsgi_server.serve_forever)
	print("done")

	print('starting connmon thread', end='...')
	t_connmon = socketio.start_background_task(obd.thread)
	print("done")

	print('starting logger thread', end='...')
	t_logger = socketio.start_background_task(data_logger.thread)
	print("done")

	def clean_shutdown():
		print("closing logger thread", end="...")
		data_logger.exit()	# tell the thread to shut down cleanly
		t_logger.join()		# wait for the thread to stop
		print("done")

		print("closing obd thread", end="...")
		obd.exit()
		t_connmon.join()
		print("done")

		print("closing server thread", end="...")
		wsgi_server.shutdown()
		t_server.join()
		print("done")

		exit(0)

	# cleanly shut down the server on exit or on Ctrl+C
	atexit_register(clean_shutdown)
	signal(SIGINT, lambda s, f: clean_shutdown())

	# keep the main thread alive
	while True:
		sleep(1)
