from flask import Flask, render_template, request, session, Response, redirect, jsonify
from socket import gethostname
from flask_socketio import SocketIO, emit
from cpuusage import CpuUsage

# import obd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'RAAAH SECRET'

socketio = SocketIO(app, logger=app.logger, engineio_logger=app.logger)


# STATIC ASSETS, MOVE THESE -------------------------------
# @app.route('/static/js/<filename>')
# def js(filename):
# 	with open('templates/static/js/' + filename) as f:
# 		return Response(f.read(), mimetype='text		ip = '10.42.0.1'/javascript')


class Dummy:
	def __init__(self):
		self.sensors = [
			{
				'id': '1',
				'name': 'da alterlator'
			},

			{
				'id': '2',
				'name': 'da sparktubes'
			},

			{
				'id': '3',
				'name': 'da belt milk'
			}
		]


dummy = Dummy()


@app.route('/')
def index():
	return render_template('main.html')


@app.route('/templates/card/selectsensors.html')
def card_selectsensors():
	return render_template('card/selectsensors.html', sensors=dummy.sensors)


@app.route('/forms/selectsensors', methods=['POST'])
def form_selectsensors():
	if request.method == 'POST':
		selected = request.form.getlist('chkSensors')
		#sensors = {key: dummy.sensors[key] for key in selected}
		sensors = [s for s in dummy.sensors if s['id'] in selected]
		return render_template('card/logging.html', sensors=sensors)


# @app.route('/templates/card/logging.html')
# def card_logging():
# 	return render_template('card/logging.html', sensors=dummy.sensors)


# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(response):
	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	response.headers['Cache-Control'] = 'public, max-age=0'
	return response


if __name__ == '__main__':
	# app.run(debug=True)

	if gethostname() == 'raspberrypi':
		ip = '100.103.188.37'
		#ip = '10.42.0.1'
	else:
		ip = '127.0.0.1'

	# app.run(host=ip)
	app.logger.setLevel('DEBUG')
	socketio.run(app, host=ip, allow_unsafe_werkzeug=True, debug=True)
