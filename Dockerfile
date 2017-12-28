# basics from https://github.com/docker/labs/blob/master/beginner/flask-app/Dockerfile
# our base image
FROM  ubuntu:17.04

#install libs necessary for Pillow to be pip installed (build from source)
RUN apt update
RUN apt install -y python3.6 python3-pip

# install Python modules needed by the Python app
COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

# copy files required for the app to run
COPY app.py /usr/src/app/
COPY config.py /usr/src/app/
COPY templates /usr/src/app/templates
COPY static /usr/src/app/static

# tell the port number the container should expose
EXPOSE 5000

#change directory so we can find our files with os.path.join
WORKDIR "/usr/src/app/"

# run the application
CMD ["python3", "app.py"]
