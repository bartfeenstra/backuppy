FROM rastasheep/ubuntu-sshd:18.04

RUN apt-get update \
    && apt-get install -y rsync \
    # Clean caches for a smaller build.
    && apt-get autoremove \
    && apt-get clean \
    && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/*
