FROM python:latest

RUN mkdir /app
WORKDIR /app
ADD . /app/

# set default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        python3-setuptools \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        && \
    dpkg --add-architecture i386 && \
    apt-get clean && \
    apt-get update && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get install -y libsm6 libxext6 libxrender-dev

RUN apt-get update ##[edited]
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y

RUN pip3 install --upgrade pip

# Install project dependencies
RUN pip3 install -r requirements.txt

RUN pip3 freeze && echo "done"

EXPOSE 80

CMD cd src && python app.py
