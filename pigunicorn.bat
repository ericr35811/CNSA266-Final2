@echo off

set proj_dir=/home/eric/CNSA266-Final
set conda_path=/home/eric/miniforge3/condabin
set branch=webpage-4-8
set pidfile=gunicorn.pid

REM pull repository and start gunicorn via ssh

set c=cd %proj_dir%
set c=%c% ^^^&^^^& git pull origin %branch%
set c=%c% ^&^& PIDFILE=%pidfile% PATH=$PATH:%conda_path% %proj_dir%/start.sh -d

start /wait ssh eric@raspberrypi "%c%"

set c=cd %proj_dir%
set c=%c% ^^^&^^^& cat %pidfile% ^^^| xargs kill
set c=%c% ^&^& rm %pidfile%

start /wait ssh eric@raspberrypi "%c%"