FROM ubuntu:18.10

RUN apt-get update && apt-get install -y rabbitmq-server \
  maxima \
  python2.7 python2.7-dev python-pip gfortran libopenblas-dev liblapack-dev \
  supervisor rabbitmq-server \
  && pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy in the app directory, although we're binding this dir in run_disting.sh
# as well to allow hot modification (FIXME: consider doing one or the other)
COPY . /app

# the main DISTING webserver port
EXPOSE 5580
# the supervisord management site's port
EXPOSE 9001

COPY supervisord.conf /etc/supervisor/supervisord.conf
CMD ["/app/entrypoint.sh"]
