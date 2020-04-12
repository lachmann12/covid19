#
# flask server for COVID-19 prediction server
#
FROM ubuntu:18.04
LABEL author="Alexander Lachmann"

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update
RUN apt-get install -y python python-pip wget vim

RUN apt-get -y install docker.io

RUN pip install Flask requests werkzeug Flask_cors waitress
RUN pip install numpy pandas
RUN pip install Flask requests
RUN pip install scipy
RUN pip install statistics

ADD app.py /home/app.py
ADD utils.py /home/utils.py
ADD templates /home/templates
COPY data /home/data

EXPOSE 5000
WORKDIR /home

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
