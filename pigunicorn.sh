#!/bin/bash

proj_dir='/home/eric/CNSA266-Final'
conda_path='/home/eric/miniforge3/condabin'
branch='webpage-4-8'
pidfile='gunicorn.pid'

start_cmd="
  cd $proj_dir
  && git pull origin $branch
  && PIDFILE=$pidfile PATH=\$PATH:$conda_path $proj_dir/start.sh -d
"

stop_cmd="
  cd $proj_dir
  && cat $pidfile | xargs kill
  && rm $pidfile
"

ssh eric@raspberrypi $start_cmd
ssh eric@raspberrypi $stop_cmd

