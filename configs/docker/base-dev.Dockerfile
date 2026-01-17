FROM debian:bookworm-slim

ARG USERNAME=devuser
ARG UID=1000
ARG GID=1000

# Install essential packages + SSH + sudo
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y sudo openssh-client openssh-server ca-certificates build-essential zsh tree git curl wget vim neovim redis-tools postgresql-client gnupg socat && \
    # Modern GPG key handling for MongoDB (apt-key is deprecated)
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc -o /tmp/mongodb-server-7.0.asc && \
    gpg --dearmor -o /etc/apt/keyrings/mongodb-server-7.0.gpg < /tmp/mongodb-server-7.0.asc && \
    chmod a+r /etc/apt/keyrings/mongodb-server-7.0.gpg && \
    # Detect architecture dynamically for MongoDB repository
    echo "deb [signed-by=/etc/apt/keyrings/mongodb-server-7.0.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" > /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update -y && \
    apt-get install -y mongodb-mongosh && \
    rm -rf /var/lib/apt/lists/* /tmp/mongodb-server-7.0.asc

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
# Copy from build context (works during build) - keys are baked into image
# Only copies *.pub files, skipping .keep and other non-key files
COPY public-ssh-keys/*.pub /tmp/ssh-keys/
RUN cat /tmp/ssh-keys/*.pub > /home/${USERNAME}/.ssh/authorized_keys 2>/dev/null || true && \
    if [ -s /home/${USERNAME}/.ssh/authorized_keys ]; then \
        chmod 600 /home/${USERNAME}/.ssh/authorized_keys && \
        chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys; \
    else \
        rm -f /home/${USERNAME}/.ssh/authorized_keys; \
    fi && \
    rm -rf /tmp/ssh-keys

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
# Only prints messages in interactive shells to avoid breaking SSH authentication
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

# NOTE: Host access from container removed - the previous implementation was fundamentally broken.
# It tried to run 'docker exec' from inside the container to access the host, which doesn't work.
# For host access, use proper Docker bind mounts or SSH from host to container instead.

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

