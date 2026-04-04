FROM vde-base:latest

# Build-time arguments
ARG PKGS_TO_INSTALL=""
ARG CUSTOM_BUILD_CMD=""

USER root

# 1. Install standard packages as root
RUN if [ -n "${PKGS_TO_INSTALL}" ]; then \
        apt-get update && \
        apt-get upgrade -y && \
        apt-get install -y ${PKGS_TO_INSTALL} && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# 2. Run custom build command (Special Forces / Hybrid)
# Note: For user-specific installs (Rust/Flutter), the command should use 'su devuser -c'
COPY scripts/ /vde/scripts/
RUN chmod +x /vde/scripts/setup/*.zsh 2>/dev/null || true
RUN if [ -n "${CUSTOM_BUILD_CMD}" ]; then \
        eval "${CUSTOM_BUILD_CMD}"; \
    fi

# 3. Switch back to root to allow SSHD to start
USER root
WORKDIR /home/devuser/workspace
CMD ["/usr/sbin/sshd", "-D", "-e"]

