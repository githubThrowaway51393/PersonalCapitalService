FROM ubuntu:18.04
MAINTAINER githubThrowaway51393
RUN apt-get update -y
RUN apt install -y python3.8
RUN apt install -y python3-pip python-dev build-essential
RUN python3.8 --version
ADD . /flask-app
WORKDIR /flask-app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["pers-cap-svc.py"]