from flask import Flask, render_template
from flask import redirect, url_for, request, session

app = Flask(__name__)

# needed for session
app.secret_key = "HEEEHEEHE SECRET"

# display text
#@app.route('/')
#def index():
#    return 'Hello world'

# pass data from the URL
@app.route('/<name>')
def print_name(name):
    return 'Hello, {}'.format(name)

@app.route('/')
def indexhtml():
    return render_template("index.jinja", content="yippee!!!!", flag=True)

@app.route('/gonk')
def gonk():
    return render_template("childtemplate.jinja")

@app.route('/post', methods=['POST', 'GET'])
def postpage():
    if request.method == 'POST':
        # get control value from form
        username = request.form['nm']
        # create a URL for the function "user" and pass it a variable
        # then redirect the client to it
        return redirect(url_for("user", uname=username))
    else:
        return render_template("post.jinja")

@app.route('/post/<uname>')
def user(uname):
    return "<h1>" + uname + "</h1>"


@app.route('/session', methods=['POST', 'GET'])
def sessionwrite():
    if request.method == 'POST':
        # get control value from form
        username = request.form['nm']
        # create a URL for the function "user" and pass it a variable
        # then redirect the client to it
        session['nm'] = username
        return redirect('/session/view')

    else:
        return render_template("post.jinja")

@app.route('/session/view')
def sessionview():
    return "<h1>Your name is " + session['nm'] + "</h1>"

if __name__ == '__main__':
    # run app
    # FLASK_APP=app.py
    # python2 -m flask run
    
    # app.run()

    # debug - reloads changes automatically
    # FLASK_DEBUG=1
    app.run(debug=True)\
