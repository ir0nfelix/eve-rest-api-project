import multiprocessing

import os

bind = "0.0.0.0:5000"

workers = os.environ.get('GUNICORN_WORKER_COUNT', multiprocessing.cpu_count() + 1)

threads = workers
user = 'eve'
group = 'eve'
worker_class = 'sync'
max_requests = 1000
max_requests_jitter = 100
accesslog = '-'
errorlog = '-'
