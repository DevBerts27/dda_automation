FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "DDA_docker_auto.py"]
