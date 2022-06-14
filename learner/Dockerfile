# This Dockerfile builds the image of Cannypot Learner
# You should decide your configuration of the Learner before building the image in etc/cowrie.cfg
# Build and run the docker image using the guide inside docker/README

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


# Set up prereqs
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
      # Added vim for modifying code and/or configurations directly inside the container
      vim \
      libsnappy-dev && \
    rm -rf /var/lib/apt/lists/*


RUN mkdir -p $WORKDIR/learner/
COPY --chown=${COWRIE_USER}:${COWRIE_GROUP} . $WORKDIR/learner/

USER ${COWRIE_USER}

RUN chmod +x ./$WORKDIR/learner/install_learner.sh && ./$WORKDIR/learner/install_learner.sh ${COWRIE_HOME}

WORKDIR ${COWRIE_HOME}


# All data that need to persit should be here: "/opt/learner/cowrie/var", "/opt/learner/cowrie/etc"
# If you want to persist data, you need to run the image specifying the volumes
# So that you can map them to the volumes (e.g., "/data/cannypot/var" and "/data/cannypot/etc")
# Before you need to copy the initial content of these folders (follow docker/README instructions)


RUN chown -R ${COWRIE_USER}:${COWRIE_USER} /opt/learner/cowrie/var/ && \
    chown -R ${COWRIE_USER}:${COWRIE_USER} /opt/learner/cowrie/etc/

VOLUME [ "/opt/learner/cowrie/var", "/opt/learner/cowrie/etc"]

USER ${COWRIE_USER}
WORKDIR ${COWRIE_HOME}/cowrie

ENV PATH=${COWRIE_HOME}/cannypot-env/bin:${PATH}
ENV PYTHONPATH=${COWRIE_HOME}/cowrie/src
ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "/opt/learner/cannypot-env/bin/python3" ]
CMD [ "/opt/learner/cannypot-env/bin/twistd", "-n", "--umask=0022", "--pidfile=", "--logger", "cowrie.python.logfile.logger" , "cowrie" ]

# Probably only 2222 is useful
EXPOSE 2222 2223