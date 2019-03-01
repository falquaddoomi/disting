#!/bin/bash

if [ -z "$ADMIN_USER" ] || [ -z "$ADMIN_PASS" ]; then
  echo "ERROR: You must supply values for the environment variables ADMIN_USER and ADMIN_PASS"
  echo "Either pass them in when you invoke docker, or create an .env file and pass it into docker via --env-file .env"
  exit -1
fi

cd /app
python manage.py syncdb --noinput && python manage.py migrate

/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
