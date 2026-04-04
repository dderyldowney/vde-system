# VDE-BASE (The Hub)
FROM debian:bookworm-slim
LABEL project="vde" component="hub"

# 1. Absolute OS Baseline
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    sudo \
    openssh-server \
    zsh \
    git \
    curl \
    wget \
    build-essential \
    procps \
    locales \
    && rm -rf /var/lib/apt/lists/*

# 2. Locale & Identity Setup
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

RUN useradd -ms /bin/zsh -u 1000 devuser && \
    echo "devuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 3. SSH Server Configuration (The Gate)
RUN mkdir -p /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# 4. The Student Environment (Oh-My-Zsh)
USER devuser
WORKDIR /home/devuser

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# 5. SSH Key Preparation
# We create the directory; the CLI 'vde-bootstrap' will handle key injection.
RUN mkdir -p /home/devuser/.ssh && chmod 700 /home/devuser/.ssh

WORKDIR /home/devuser/workspace
CMD ["sudo", "/usr/sbin/sshd", "-D"]

