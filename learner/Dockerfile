# This Dockerfile contains the image for Cannypot
# Decide your configuration of Cannypot before building the image
# Run this dockerfile using the guide inside docker/README

ARG http_proxy
ARG https_proxy

ARG ARCH=
ARG BUILD_DATE
ARG TAG
FROM ${ARCH}ubuntu:20.04 as builder

WORKDIR /

# This is a temporary workaround, see https://github.com/cowrie/docker-cowrie/issues/26
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

ENV COWRIE_GROUP=cowrie \
    COWRIE_USER=cowrie \
    COWRIE_HOME=/opt/learner



# Not working locales
#RUN apt-get install -y locales locales-all

# Set locale to UTF-8, otherwise upstream libraries have bytes/string conversion issues
ENV LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8


LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.authors="Giulia Milan <giulia.milan@huawei.com>"
LABEL org.opencontainers.image.source="https://github.com/SmartData-Polito/cannypot"
LABEL org.opencontainers.image.version="${TAG}"
LABEL org.opencontainers.image.vendor="Huawei"
LABEL org.opencontainers.image.title="Cannypot"
LABEL org.opencontainers.image.description="SSH RL Honeypot"

RUN groupadd -r ${COWRIE_GROUP} && \
    useradd -u 1500 -r -d ${COWRIE_HOME} -m -g ${COWRIE_GROUP} ${COWRIE_USER}


# Are all these packages necessary?
# Set up Debian prereqs
RUN export DEBIAN_FRONTEND=noninteractive; \
      apt-get -y update && \
      apt-get -y upgrade && \  
      apt-get -y install \
        -o APT::Install-Suggests=false \
        -o APT::Install-Recommends=false \
       --fix-missing \
      python3-pip \
      ca-certificates \
      libffi-dev \
      libssl-dev \
      python3-dev \
      python3-venv \
      python3 \ 
      #rustc \
      #cargo \
      git \
      build-essential \
      python3-virtualenv \
      # Added vim for modifying code directly inside the container
      vim \
      libsnappy-dev && \
    rm -rf /var/lib/apt/lists/*


RUN mkdir -p $WORKDIR/learner/
COPY --chown=${COWRIE_USER}:${COWRIE_GROUP} . $WORKDIR/learner/

USER ${COWRIE_USER}

RUN chmod +x ./$WORKDIR/learner/install_learner.sh && ./$WORKDIR/learner/install_learner.sh ${COWRIE_HOME}

WORKDIR ${COWRIE_HOME}


# All necessary data to persit should be here
# I want to map them into /data/cannypot/var/log and /data/cannypot/etc
# Copy the initial content (to know the configuration of cannypot) and then run with volumes in the run command


RUN chown -R ${COWRIE_USER}:${COWRIE_USER} /opt/learner/cowrie/var/ && \
    chown -R ${COWRIE_USER}:${COWRIE_USER} /opt/learner/cowrie/etc/

VOLUME [ "/opt/learner/cowrie/var", "/opt/learner/cowrie/etc"]

USER ${COWRIE_USER}
WORKDIR ${COWRIE_HOME}/cowrie

ENV PATH=${COWRIE_HOME}/cannypot-env/bin:${PATH}
ENV PYTHONPATH=${COWRIE_HOME}/cowrie/src
ENV PYTHONUNBUFFERED=1

#ENTRYPOINT [ "/cowrie/cowrie-env/bin/python3" ]
#CMD [ "/opt/learner/cowrie/bin/cowrie", "start"]

ENTRYPOINT [ "/opt/learner/cannypot-env/bin/python3" ]
#CMD [ "/opt/learner/cannypot-env/bin/twistd", "-n", "--umask=0022", "--pidfile=" , "cowrie" ]
CMD [ "/opt/learner/cannypot-env/bin/twistd", "-n", "--umask=0022", "--pidfile=", "--logger", "cowrie.python.logfile.logger" , "cowrie" ]

EXPOSE 2222 2223