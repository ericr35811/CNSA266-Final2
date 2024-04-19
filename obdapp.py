from flask import Flask, render_template, request, session, Response, redirect, jsonify
from socket import gethostname
from flask_socketio import SocketIO, emit
from cpuusage import CpuUsage
import logging, logging.handlers
from queue import Queue
from obdthread import DataLogger, CarConnection
from atexit import register as atexit_register
from signal import signal, SIGINT
from werkzeug.serving import BaseWSGIServer, ThreadedWSGIServer
from time import sleep
from sys import exit

print(__name__)

# create the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'RAAAH SECRET'

# create the SocketIO app based on the Flask app
socketio = SocketIO(app, logger=app.logger, engineio_logger=app.logger, async_mode='threading')

# instantiate classes for background tasks
# CarConnection monitors the OBD connection, and DataLogger reads data from the car
# These are background tasks because they would freeze the web server
# the threads are controlled via the classes
# obd = CarConnection(socketio, test=True)
obd = CarConnection(socketio, test=True)
data_logger = DataLogger(obd, socketio)

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


@socketio.on('disconnect')
def ondisconnect():
	print('socketio client disconnected')
	data_logger.stop()


@socketio.on('car_connect')
def car_connect():
	print('Connecting to car')
	obd.connect()
	return True


@socketio.on('car_disconnect')
def car_disconnect():
	print('Disconnecting from car')
	obd.disconnect()


@socketio.on('log_start')
def start_logging():
	data_logger.start()


@socketio.on('log_stop')
def stop_logging():
	data_logger.stop()


@socketio.on('log_rate')
def log_rate(rate):
	data_logger.rate = float(rate)


if __name__ == '__main__':
	if gethostname() == 'raspberrypi':
		ip = '100.103.188.37'
		#ip = '10.42.0.1'
	else:
		ip = '127.0.0.1'

	# ip = '100.68.132.31'

	# app.run(host=ip)
	app.logger.setLevel('DEBUG')
	# socketio.run(app, host=ip, debug=True, allow_unsafe_werkzeug=True)

	wsgi_server = ThreadedWSGIServer(app=app, host=ip, port=5000)

	# create processes as SocketIO background tasks (threads)
	t_server = socketio.start_background_task(wsgi_server.serve_forever)
	t_connmon = socketio.start_background_task(obd.thread)
	t_logger = socketio.start_background_task(data_logger.thread)

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

	# keep this thread alive so it can c
	while True:
		sleep(1)




