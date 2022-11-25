#!/bin/bash
# start-server.sh
(cd /usr/src/app/italycoast; gunicorn italycoast.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"