FROM debian:bookworm-slim

ARG USERNAME=devuser
ARG UID=1000
ARG GID=1000

# Install essential packages + SSH + sudo
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y sudo openssh-client openssh-server ca-certificates build-essential zsh tree git curl wget vim neovim redis-tools postgresql-client gnupg socat && \
    wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add - && \
    echo "deb [arch=amd64,arm64] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" > /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update -y && \
    apt-get install -y mongodb-mongosh && \
    rm -rf /var/lib/apt/lists/*

# Create devuser with sudo privileges and SSH setup
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

# Copy public SSH keys into authorized_keys with proper ownership
COPY --chown=${USERNAME}:${USERNAME} public-ssh-keys/* /home/${USERNAME}/.ssh/authorized_keys
RUN chmod 600 /home/${USERNAME}/.ssh/authorized_keys

# Configure SSH server for agent forwarding and security
RUN sed -i \
    -e 's/^#PasswordAuthentication yes/PasswordAuthentication no/' \
    -e 's/^#KbdInteractiveAuthentication yes/KbdInteractiveAuthentication no/' \
    -e 's/^#ChallengeResponseAuthentication yes/ChallengeResponseAuthentication no/' \
    -e 's/^#AllowAgentForwarding yes/AllowAgentForwarding yes/' \
    /etc/ssh/sshd_config || true

# Configure SSH client for agent forwarding
RUN mkdir -p /home/${USERNAME}/.ssh && \
    echo "Host *" > /home/${USERNAME}/.ssh/config && \
    echo "    ForwardAgent yes" >> /home/${USERNAME}/.ssh/config && \
    echo "    StrictHostKeyChecking no" >> /home/${USERNAME}/.ssh/config && \
    echo "    UserKnownHostsFile /dev/null" >> /home/${USERNAME}/.ssh/config && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/config && \
    chmod 600 /home/${USERNAME}/.ssh/config

# Add SSH agent forwarding helper script
RUN echo '#!/bin/zsh' > /usr/local/bin/ssh-agent-forward && \
    echo '' >> /usr/local/bin/ssh-agent-forward && \
    echo '# Setup SSH agent forwarding from host' >> /usr/local/bin/ssh-agent-forward && \
    echo 'if [[ -n "$SSH_AUTH_SOCK" ]]; then' >> /usr/local/bin/ssh-agent-forward && \
    echo '    export SSH_AUTH_SOCK' >> /usr/local/bin/ssh-agent-forward && \
    echo '    echo "SSH agent forwarding enabled: $SSH_AUTH_SOCK"' >> /usr/local/bin/ssh-agent-forward && \
    echo 'else' >> /usr/local/bin/ssh-agent-forward && \
    echo '    echo "No SSH agent found. Start agent on host with: eval \$(ssh-agent -s) && ssh-add"' >> /usr/local/bin/ssh-agent-forward && \
    echo 'fi' >> /usr/local/bin/ssh-agent-forward && \
    chmod +x /usr/local/bin/ssh-agent-forward

# Add host access helper script (for accessing host from container)
RUN echo '#!/bin/zsh' > /usr/local/bin/host-sh && \
    echo '' >> /usr/local/bin/host-sh && \
    echo '# Execute command on host via docker exec' >> /usr/local/bin/host-sh && \
    echo 'host_cmd() {' >> /usr/local/bin/host-sh && \
    echo '    local container_name=$(/bin/hostname)' >> /usr/local/bin/host-sh && \
    echo '    docker exec -it "$container_name" "$@" 2>/dev/null || echo "Cannot access host from container"' >> /usr/local/bin/host-sh && \
    echo '}' >> /usr/local/bin/host-sh && \
    echo '' >> /usr/local/bin/host-sh && \
    echo 'alias to-host=host_cmd' >> /usr/local/bin/host-sh && \
    chmod +x /usr/local/bin/host-sh && \
    echo 'source /usr/local/bin/host-sh' >> /home/${USERNAME}/.zshrc

# Install oh-my-zsh, configure zsh, and setup LazyVim
RUN su ${USERNAME} -c 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended' && \
    echo 'export PATH=$HOME/.local/bin:$PATH' > /home/${USERNAME}/.zprofile && \
    echo 'export ZSH_THEME="agnoster"' >> /home/${USERNAME}/.zshrc && \
    echo 'source /usr/local/bin/ssh-agent-forward' >> /home/${USERNAME}/.zshrc && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.zprofile /home/${USERNAME}/.zshrc && \
    su ${USERNAME} -c 'git clone https://github.com/LazyVim/starter ~/.config/nvim && nvim --headless +qall'

# Expose SSH port
EXPOSE 22

# Default command to run SSH daemon
CMD ["/usr/sbin/sshd","-D"]

