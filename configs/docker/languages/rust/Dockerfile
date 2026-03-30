# Rust VM Dockerfile
# Inherits from vde-base and adds Rust toolchain at build-time
FROM vde-base:latest

ARG USERNAME=devuser

# Install Rust for devuser
# We use the official rustup script but run it as devuser to ensure proper file ownership
RUN su ${USERNAME} -c "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y" && \
    su ${USERNAME} -c ". \$HOME/.cargo/env && rustup default stable"

# Ensure Rust binaries are in the path for all shells
RUN echo 'export PATH=$HOME/.cargo/bin:$PATH' >> /home/${USERNAME}/.zshrc && \
    echo 'export PATH=$HOME/.cargo/bin:$PATH' >> /home/${USERNAME}/.zprofile

# Set environment variable for non-interactive sessions
ENV PATH=/home/${USERNAME}/.cargo/bin:${PATH}

# Entrypoint and CMD are inherited from vde-base
