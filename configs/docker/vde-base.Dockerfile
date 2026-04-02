# VDE Base Development Image
# This image is the foundation for all language and service VMs
# Built once as vde-base:latest, then extended by VM-specific Dockerfiles
FROM debian:bookworm-slim

ARG USERNAME=devuser
ARG UID=1000
ARG GID=1000
ARG PUBLIC_KEYS_DIR=/public-ssh-keys

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install essential packages + SSH + sudo + common dev tools + services
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y sudo openssh-client openssh-server ca-certificates build-essential zsh tree git curl wget vim neovim redis-server postgresql-15 postgresql-client gnupg socat iputils-ping && \
    # Setup locale
    apt-get install -y locales && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    # Create devuser
    groupadd --gid ${GID} ${USERNAME} && \
    useradd --uid ${UID} --gid ${GID} -m -s /usr/bin/zsh ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && \
    chmod 0440 /etc/sudoers.d/${USERNAME} && \
    # Configure SSH
    mkdir /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    # Create VDE entrypoint and mount directories
    mkdir -p /public-ssh-keys /ssh-agent && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create entrypoint script
RUN echo '#!/bin/zsh' > /usr/local/bin/vde-entrypoint && \
    echo 'set -e' >> /usr/local/bin/vde-entrypoint && \
    echo '' >> /usr/local/bin/vde-entrypoint && \
    echo '# Configure SSH keys from mount' >> /usr/local/bin/vde-entrypoint && \
    echo 'if [ -d /public-ssh-keys ]; then' >> /usr/local/bin/vde-entrypoint && \
    echo '    mkdir -p /home/devuser/.ssh' >> /usr/local/bin/vde-entrypoint && \
    echo '    cat /public-ssh-keys/*.pub > /home/devuser/.ssh/authorized_keys 2>/dev/null || true' >> /usr/local/bin/vde-entrypoint && \
    echo '    if [ -s /home/devuser/.ssh/authorized_keys ]; then' >> /usr/local/bin/vde-entrypoint && \
    echo '        chmod 700 /home/devuser/.ssh' >> /usr/local/bin/vde-entrypoint && \
    echo '        chmod 600 /home/devuser/.ssh/authorized_keys' >> /usr/local/bin/vde-entrypoint && \
    echo '        chown -R devuser:devuser /home/devuser/.ssh' >> /usr/local/bin/vde-entrypoint && \
    echo '    fi' >> /usr/local/bin/vde-entrypoint && \
    echo 'fi' >> /usr/local/bin/vde-entrypoint && \
    echo '' >> /usr/local/bin/vde-entrypoint && \
    echo 'exec "$@"' >> /usr/local/bin/vde-entrypoint && \
    chmod +x /usr/local/bin/vde-entrypoint

# Default command: run SSH daemon (passed as args to entrypoint)
ENTRYPOINT ["/usr/local/bin/vde-entrypoint"]
CMD ["/usr/sbin/sshd","-D"]
