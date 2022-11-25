FROM python:3.9-buster
LABEL Digital Twin Italian coasts backend django image

RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/italycoast

# Enable postgresql-client-13
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list
RUN echo "deb http://deb.debian.org/debian/ stable main contrib non-free" | tee /etc/apt/sources.list.d/debian.list
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# To get GDAL 3.2.1 to fix this issue https://github.com/OSGeo/gdal/issues/1692
# TODO: The following line should be removed if base image upgraded to Bullseye
RUN echo "deb http://deb.debian.org/debian/ bullseye main contrib non-free" | tee /etc/apt/sources.list.d/debian.list

RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# Prepraing dependencies
RUN apt-get install -y devscripts build-essential debhelper pkg-kde-tools sharutils
# RUN git clone https://salsa.debian.org/debian-gis-team/proj.git /tmp/proj
# RUN cd /tmp/proj && debuild -i -us -uc -b && dpkg -i ../*.deb

# This section is borrowed from the official Django image but adds GDAL and others
RUN apt-get install -y \
    libgdal-dev libpq-dev libxml2-dev \
    libxml2 libxslt1-dev zlib1g-dev libjpeg-dev \
    libmemcached-dev libldap2-dev libsasl2-dev libffi-dev

RUN apt-get install -y \
    gcc zip gettext geoip-bin cron \
    python3-dev python3-gdal python3-psycopg2 python3-ldap \
    python3-pip python3-pil python3-lxml python3-pylibmc \
    uwsgi uwsgi-plugin-python3 \
    firefox-esr \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*


#Copy files
COPY requirements.txt /usr/src/app/
COPY start-server.sh /usr/src/app/
COPY italycoast /usr/src/app/italycoast
RUN chown -R www-data:www-data /usr/src/app/

# Install pip packages
RUN pip install pip --upgrade
RUN pip install --upgrade -r /usr/src/app/requirements.txt \
    && pip install pygdal==$(gdal-config --version).* \
    && pip install flower==0.9.4

#RUN pip install --upgrade  -e .

EXPOSE 8000
STOPSIGNAL SIGTERM
RUN chmod +x /usr/src/app/start-server.sh
ENTRYPOINT ["/usr/src/app/start-server.sh"]
#ENTRYPOINT /usr/src/app/start-server.sh

#CMD ["/usr/src/app/start-server.sh"]
