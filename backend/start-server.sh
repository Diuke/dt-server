#!/usr/bin/env bash
# start-server.sh
if [ -n "admin" ] && [ -n "Admin123" ] ; then
    (cd italycoast; python manage.py createsuperuser --no-input)
fi
(cd italycoast; gunicorn italycoast.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"