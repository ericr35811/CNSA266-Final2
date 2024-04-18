from flask import Flask, render_template, request, session, Response, redirect, jsonify
from socket import gethostname
from flask_socketio import SocketIO, emit
from cpuusage import CpuUsage
import logging, logging.handlers
from queue import Queue
from obdthread import DataLogger, CarConnection, close_threads
from atexit import register as atexit_register
from signal import signal, SIGINT

# create the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'RAAAH SECRET'

# create the SocketIO app based on the Flask app
socketio = SocketIO(app, logger=app.logger, engineio_logger=app.logger)

# instantiate classes for background tasks
# CarConnection monitors the OBD connection, and DataLogger reads data from the car
# These are background tasks because they would freeze the web server
# the threads are controlled via the classes
# obd = CarConnection(socketio, test=True)
obd = CarConnection(socketio, test=True)
data_logger = DataLogger(obd, socketio)

# start the threads for the background tasks
# order matters
threads = [
	[data_logger.app_exit, socketio.start_background_task(data_logger.log_thread)],
	[obd.app_exit,			socketio.start_background_task(obd.connmon_thread)]
]

# make sure to close the background threads on server shutdown
atexit_register(lambda: close_threads(threads))
# do the same for CTRL-C
signal(SIGINT, lambda s, f: close_threads(threads))


# logging.getLogger().addHandler(logging.StreamHandler())


@app.route('/')
def index():
	return render_template('main.html')


@app.route('/templates/card/selectsensors.html')
def card_selectsensors():
	return render_template('card/selectsensors.html', sensors=obd.sensors)


@app.route('/forms/selectsensors', methods=['POST'])
def form_selectsensors():
	if request.method == 'POST':
		# list of PIDs representing each checked sensor
		selected = request.form.getlist('chkSensors')
		# get sensors info by PID
		sensors = [s for s in obd.sensors if s['pid'] in selected]
		data_logger.set_sensors(sensors)

		return render_template('card/logging.html', sensors=sensors)


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
	print('socketio client connected')
	# if the user reloads the page or connects for the first time, send them the connection status
	socketio.emit('car_connect_status', obd.status)


@socketio.on('car_disconnect')
def car_disconnect():
	print('Disconnecting from car')
	obd.disconnect()


@socketio.on('car_connect')
def car_connect():
	print('Connecting to car')
	obd.connect()
	return True


@socketio.on('start_logging')
def start_logging():
	data_logger.start()


if __name__ == '__main__':
	if gethostname() == 'raspberrypi':
		ip = '100.103.188.37'
		#ip = '10.42.0.1'
	else:
		ip = '127.0.0.1'

	# app.run(host=ip)
	app.logger.setLevel('DEBUG')
	socketio.run(app, host=ip, debug=True, allow_unsafe_werkzeug=True)
