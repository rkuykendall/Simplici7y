import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings - must work within Heroku's 30-second limit
timeout = 30  # Heroku's hard limit
keepalive = 2

# File upload specific settings
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance
tmp_upload_dir = None

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "simplici7y"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Preload application for better performance
preload_app = True

# Worker process lifecycle
max_requests = 1000
max_requests_jitter = 100

# Enable request ID for debugging
capture_output = True


def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    """
    Called just before a worker is forked.
    """
    pass


def when_ready(server):
    """
    Called just after the server is started.
    """
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    """
    Called just after a worker exited on SIGINT or SIGQUIT.
    """
    worker.log.info("worker received INT or QUIT signal")


def pre_exec(server):
    """
    Called just before a new master process is forked.
    """
    server.log.info("Forked child, re-executing.")
