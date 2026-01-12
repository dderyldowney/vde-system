FROM postgres:latest

ARG USERNAME=devuser
ARG UID=1000
ARG GID=1000
ARG PUBLIC_KEYS_DIR=/public-ssh-keys

# Install SSH and sudo
RUN apt-get update -y && \
    apt-get install -y ssh openssh-server sudo && \
    rm -rf /var/lib/apt/lists/*

# Create devuser (Linux user for SSH)
RUN groupadd -g ${GID} ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && \
    chmod 440 /etc/sudoers.d/${USERNAME}

# SSH setup
RUN mkdir -p /var/run/sshd
RUN mkdir -p /home/${USERNAME}/.ssh && chmod 700 /home/${USERNAME}/.ssh && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh

# Copy public keys for SSH login
COPY public-ssh-keys/* /home/${USERNAME}/.ssh/authorized_keys
RUN chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys && \
    chmod 600 /home/${USERNAME}/.ssh/authorized_keys

# Optional: disable password authentication for SSH (recommended after testing)
RUN sed -i \
    -e 's/^#PasswordAuthentication yes/PasswordAuthentication no/' \
    -e 's/^#KbdInteractiveAuthentication yes/KbdInteractiveAuthentication no/' \
    -e 's/^#ChallengeResponseAuthentication yes/ChallengeResponseAuthentication no/' \
    /etc/ssh/sshd_config || true


# Default command for postgres container
CMD /usr/sbin/sshd && \
    exec /usr/local/bin/docker-entrypoint.sh postgres

