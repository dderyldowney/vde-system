# MongoDB-specific base image that renames ubuntu user to devuser
# This is needed because mongo:latest already has ubuntu:1000:1000
ARG BASE_IMAGE=mongo:latest
FROM ${BASE_IMAGE}

ARG USERNAME=devuser
ARG ORIGINAL_USER=ubuntu

# Install SSH, sudo, and zsh
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Rename ubuntu user to devuser (preserves UID/GID 1000:1000)
RUN usermod -l ${USERNAME} ${ORIGINAL_USER} && \
    usermod -d /home/${USERNAME} -m ${USERNAME} && \
    groupmod -n ${USERNAME} ${ORIGINAL_USER}

# Change shell to zsh
RUN chsh -s /bin/zsh ${USERNAME}

# Create SSH directory
RUN mkdir -p /home/${USERNAME}/.ssh && \
    chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh && \
    chmod 700 /home/${USERNAME}/.ssh

# Copy SSH public keys
COPY --chown=${USERNAME}:${USERNAME} public-ssh-keys /tmp/ssh-keys/

# Setup authorized_keys
RUN cat /tmp/ssh-keys/*.pub > /home/${USERNAME}/.ssh/authorized_keys && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys && \
    chmod 600 /home/${USERNAME}/.ssh/authorized_keys && \
    rm -rf /tmp/ssh-keys

# Disable password authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Create SSH privilege separation directory
RUN mkdir -p /run/sshd

EXPOSE 22
CMD /usr/sbin/sshd && \
    exec docker-entrypoint.sh mongod
