import flask

app = flask.Flask(__name__)

#app.secret_key=

@app.route('/')
def index():
    return 'hallo'

if __name__ == '__main__':
    app.run(debug=True)
