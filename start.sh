#!/bin/bash

if [ -z "$PIDFILE" ]
then
	PIDFILE=gunicorn.pid
fi

if [ $1- == '-d-' ]
then
	# debug output with -d switch
	conda run -n CNSA266-Final-py3 --live-stream gunicorn --pid $PIDFILE --config gunicorn.conf.py app:app
#	rm $PIDFILE
else
	conda run -n CNSA266-Final-py3 gunicorn --pid $PIDFILE --config gunicorn.conf.py app:app
#	rm $PIDFILE
fi



