FROM osgeo/gdal:ubuntu-small-latest

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update
RUN apt-get install -y software-properties-common && apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

# RUN add-apt-repository ppa:ubuntugis/ppa &&  apt-get update
# RUN apt-get install -y gdal-bin libgdal-dev
# ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
# ARG C_INCLUDE_PATH=/usr/include/gdal
# RUN pip install GDAL

# We copy just the requirements.txt first to leverage Docker cache
COPY /requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app
EXPOSE 80
# CMD [ "gunicorn", "-b", "0.0.0.0:8000", "wsgi:app", "--timeout 200", "-w 2" ,"--threads 2" ]
ENTRYPOINT [ "python3" ]

CMD [ "app/app.py" ]
