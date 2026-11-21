# Loaded automatically by gunicorn from the working directory.
# Worker count comes from WEB_CONCURRENCY (set on Railway).

# Threaded workers: a slow upload occupies one thread, not a whole worker,
# and long requests aren't killed by the worker timeout (the main thread
# keeps checking in while request threads work).
worker_class = "gthread"
threads = 4

# Railway allows request bodies up to 5 minutes and requests up to 15. The
# old sync workers were killed after gunicorn's default 30s, which is what
# broke large uploads.
timeout = 300
graceful_timeout = 30
