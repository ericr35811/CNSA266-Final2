from flask import Flask, render_template, request, session
from psutil import cpu_percent
from datetime import datetime

app = Flask(__name__)

app.secret_key='supersecret'

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		elapsed = (datetime.now() - session['t0']).strftime('%H:%M:%S:%f')[:-4]
		percent = str(round(cpu_percent(), 1))
		print(percent)
		return elapsed + '|' + percent
	else:
		session['t0'] = datetime.now()
		return render_template('main.html')

if __name__ == '__main__':
	app.run(debug=True)
