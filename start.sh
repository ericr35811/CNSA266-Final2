#!/bin/bash

if [ $1- == '-d-' ]
then
	# debug output with -d switch
	conda run -n py2test --live-stream gunicorn --pid $PIDFILE --config gunicorn.conf.py app:app
else
	conda run -n py2test gunicorn --pid $PIDFILE --config gunicorn.conf.py app:app
fi



