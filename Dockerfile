# ubuntu:18.04
FROM ubuntu@sha256:122f506735a26c0a1aff2363335412cfc4f84de38326356d31ee00c2cbe52171

LABEL maintainer="Brazil Data Cube Team <brazildatacube@inpe.br>"

# Setup build env for PROJ
USER root
RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing --no-install-recommends \
            software-properties-common build-essential ca-certificates \
            git make cmake wget unzip libtool automake \
            zlib1g-dev libsqlite3-dev pkg-config sqlite3 libcurl4-gnutls-dev \
            libtiff5-dev \
    && apt install python3-pip -y \
    && apt install nano \
    && rm -rf /var/lib/apt/lists/*

RUN apt install python3-pip

RUN mkdir /app

# s2-angs
COPY . /app/s2angs
WORKDIR /app/s2angs
RUN pip3 install .

RUN mkdir /code

COPY docker_entrypoint.py /code

WORKDIR /work

### Run the sen2cor application
ENTRYPOINT ["python3", "/code/docker_entrypoint.py"]