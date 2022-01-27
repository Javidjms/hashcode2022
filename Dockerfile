FROM python:3.9.2-buster AS base-dev

# Initial Work Directory
WORKDIR /data

# Install apt packages
RUN apt-get update && apt-get install -y \
    gcc \
    musl-dev \
    build-essential \
    libpq-dev \
    libffi-dev \
    openssl \
    libssl-dev \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


# Install pip packages
COPY requirements.txt /data/requirements.txt
RUN pip install -r requirements.txt

# Copy source files
COPY . .

# Keep container awake
CMD ["tail", "-f", "/dev/null"]
