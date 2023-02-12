#!/bin/bash
#exec gunicorn --certfile=origin.pem --keyfile=key.pem --worker-class gevent --bind 0.0.0.0:443 app:app
exec gunicorn --worker-class gevent --bind 0.0.0.0:6000 app:app