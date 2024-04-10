@echo off

REM pull repository and start gunicorn via ssh
start /wait ssh eric@raspberrypi "cd /home/eric/CNSA266-Final && git pull origin webpage-4-8 && PATH=$PATH:/home/eric/miniforge3/condabin ~/CNSA266-Final/start.sh -d"

start /wait ssh eric@raspberrypi "cd /home/eric/CNSA266-Final && cat gunicorn.pid | xargs kill"


REM kill gunicorn after previous command finishes
