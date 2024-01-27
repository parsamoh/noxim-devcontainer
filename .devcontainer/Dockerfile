FROM --platform=linux/amd64 python:3.12.1-alpine3.19

RUN apk update && \
    apk add ca-certificates

RUN apk add --update --no-cache \
    ca-certificates \
    wget \
    build-base \
    sudo \
    tar \
    boost-dev \
    cmake \
    git \
    && rm -rf /var/cache/apk/*

WORKDIR /opt/

RUN wget https://github.com/davidepatti/noxim/archive/master.zip -O master.zip && \
    unzip master.zip && \
    mv noxim-master noxim

RUN mkdir -p noxim/bin/libs && \
    cd noxim/bin/libs && \
    git clone https://github.com/jbeder/yaml-cpp && \
    cd yaml-cpp && \
    git checkout -b r0.6.0 yaml-cpp-0.6.0 && \
    mkdir -p lib && \
    cd lib && \
    cmake .. && \
    make

ENV LD_LIBRARY_PATH=/opt/noxim/bin/libs/systemc-2.3.1/lib-linux64 \
    CXX=g++ \
    CC=gcc

RUN cd noxim/bin/libs && \
    wget http://www.accellera.org/images/downloads/standards/systemc/systemc-2.3.1.tgz && \
    tar -xzf systemc-2.3.1.tgz && \
    cd systemc-2.3.1 && \
    mkdir -p objdir && \
    cd objdir && \
    ../configure && \
    make && \
    make install && \
    cd .. && \
    echo `pwd`/lib-* > systemc.conf && \
    ldconfig systemc.conf

RUN cd /opt/noxim/bin && \
    make && \
    ln -s /opt/noxim/bin/noxim /usr/local/bin/noxim

ENTRYPOINT ["/bin/ash"]