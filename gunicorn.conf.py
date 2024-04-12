from multiprocessing import cpu_count

# base options
bind = '100.103.188.37:5000'
workers = cpu_count() * 2 + 1

# debug options
reload = True
  # - means log to stdout
accesslog = '-'
access_log_format = '%(h)s %(l)s %(t)s (%(r)s) %(s)s %(f)s'

errorlog = '-'
loglevel = 'info'
