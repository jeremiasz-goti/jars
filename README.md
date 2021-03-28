# Jars Api

Simple wallet system.

## Features

- Create Jars with currency attached
- Deposit and withdraw resources from jar
- Transfer resources between jars
- Display and sort history of jar operations

## Tech

Jars is using:

- [Python 3.8](https://www.python.org/)
- [FastApi](https://fastapi.tiangolo.com/)


## Installation

# Local

Clone repository

```sh
git clone https://github.com/jeremiasz-goti/jars.git
```

Install dependencies and run

```sh
cd jars
pip install -r requirements.txt
cd src
uvicorn main:app --reload
```

# Docker

To deploy Jars in a Docker container use:

```sh
cd jars
docker build -t jars:1.0 .
```

By default, the Docker will expose port 8080, so change this within the
Dockerfile if necessary. When ready, simply use the Dockerfile to
build the image.

Once done, run the Docker image and map the port to whatever you wish on
your host. In this example, we simply map port 8000 of the host to
port 8000 of the Docker (or whatever port was exposed in the Dockerfile):

```sh
docker run -d --name jars-container -p 8000:8000 jars:1.0
```

Verify the deployment by navigating to your server address in
your preferred browser.

```sh
127.0.0.1:8000
```
