FROM microservice_python
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN pip install -U paramiko
RUN apt-get install -y rsync ssh

ADD ./supervisor/vagrant.conf /etc/supervisor/conf.d/vagrant.conf
ADD . /opt/vagrant
RUN chmod 600 /opt/vagrant/config/*.key
RUN python /opt/vagrant/src/build.py

EXPOSE 80
