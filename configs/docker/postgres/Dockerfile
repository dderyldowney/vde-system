# Hybrid approach: Use official postgres image + full base-dev devuser setup
FROM postgres:latest

ARG USERNAME=devuser
ARG UID=1000
ARG GID=1000

# Install essential packages from base-dev (SSH, sudo, zsh, tools)
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y sudo openssh-client openssh-server ca-certificates \
        build-essential zsh tree git curl wget vim neovim redis-tools \
        postgresql-client gnupg socat && \
    rm -rf /var/lib/apt/lists/*

# Create devuser with sudo privileges (matching base-dev exactly)
RUN groupadd -g ${GID} ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -s /bin/zsh ${USERNAME} && \
    usermod -aG sudo ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && \
    chmod 440 /etc/sudoers.d/${USERNAME} && \
    mkdir -p /var/run/sshd && \
    mkdir -p /home/${USERNAME}/.ssh && \
    touch /home/${USERNAME}/.ssh/known_hosts && \
    chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh && \
    chmod 700 /home/${USERNAME}/.ssh && \
    chmod 600 /home/${USERNAME}/.ssh/known_hosts

# Copy public SSH keys into authorized_keys (matching base-dev exactly)
COPY public-ssh-keys/*.pub /tmp/ssh-keys/
RUN cat /tmp/ssh-keys/*.pub > /home/${USERNAME}/.ssh/authorized_keys 2>/dev/null || true && \
    if [ -s /home/${USERNAME}/.ssh/authorized_keys ]; then \
        chmod 600 /home/${USERNAME}/.ssh/authorized_keys && \
        chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys; \
    else \
        rm -f /home/${USERNAME}/.ssh/authorized_keys; \
    fi && \
    rm -rf /tmp/ssh-keys

# Configure SSH server for agent forwarding (matching base-dev exactly)
RUN sed -i \
    -e 's/^#PasswordAuthentication yes/PasswordAuthentication no/' \
    -e 's/^#KbdInteractiveAuthentication yes/KbdInteractiveAuthentication no/' \
    -e 's/^#ChallengeResponseAuthentication yes/ChallengeResponseAuthentication no/' \
    -e 's/^#AllowAgentForwarding yes/AllowAgentForwarding yes/' \
    /etc/ssh/sshd_config || true

# Configure SSH client for agent forwarding (matching base-dev exactly)
RUN mkdir -p /home/${USERNAME}/.ssh && \
    echo "Host *" > /home/${USERNAME}/.ssh/config && \
    echo "    ForwardAgent yes" >> /home/${USERNAME}/.ssh/config && \
    echo "    StrictHostKeyChecking no" >> /home/${USERNAME}/.ssh/config && \
    echo "    UserKnownHostsFile /dev/null" >> /home/${USERNAME}/.ssh/config && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/config && \
    chmod 600 /home/${USERNAME}/.ssh/config

# Add SSH agent forwarding helper script (matching base-dev exactly)
RUN echo '#!/bin/zsh' > /usr/local/bin/ssh-agent-forward && \
    echo '' >> /usr/local/bin/ssh-agent-forward && \
    echo '# Setup SSH agent forwarding from host' >> /usr/local/bin/ssh-agent-forward && \
    echo '# Only print messages in interactive shells (tty check)' >> /usr/local/bin/ssh-agent-forward && \
    echo 'if [[ -n "$SSH_AUTH_SOCK" ]]; then' >> /usr/local/bin/ssh-agent-forward && \
    echo '    export SSH_AUTH_SOCK' >> /usr/local/bin/ssh-agent-forward && \
    echo '    [[ -t 1 ]] && echo "SSH agent forwarding enabled: $SSH_AUTH_SOCK"' >> /usr/local/bin/ssh-agent-forward && \
    echo 'else' >> /usr/local/bin/ssh-agent-forward && \
    echo '    [[ -t 1 ]] && echo "No SSH agent found. Start agent on host with: eval \$(ssh-agent -s) && ssh-add"' >> /usr/local/bin/ssh-agent-forward && \
    echo 'fi' >> /usr/local/bin/ssh-agent-forward && \
    chmod +x /usr/local/bin/ssh-agent-forward

# Install oh-my-zsh, configure zsh (LazyVim skipped for service VMs - not essential)
RUN su ${USERNAME} -c 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended' && \
    echo 'export PATH=$HOME/.local/bin:$PATH' > /home/${USERNAME}/.zprofile && \
    echo 'export ZSH_THEME="agnoster"' >> /home/${USERNAME}/.zshrc && \
    echo 'source /usr/local/bin/ssh-agent-forward' >> /home/${USERNAME}/.zshrc && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.zprofile /home/${USERNAME}/.zshrc

# Expose PostgreSQL port (official image already exposes 5432, but explicit is clearer)
EXPOSE 5432

# Start SSH daemon and then the official postgres entrypoint
# This preserves all official postgres image benefits (init scripts, data dir setup, etc.)
CMD ["/bin/bash", "-c", "/usr/sbin/sshd && exec /usr/local/bin/docker-entrypoint.sh postgres"]
