# PostgreSQL VM Dockerfile
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y postgresql && \
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/15/main/postgresql.conf && \
    echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/15/main/pg_hba.conf && \
    echo "host all all 0.0.0.0/0 trust" >> /etc/postgresql/15/main/pg_hba.conf && \
    rm -rf /var/lib/apt/lists/*

# Use a startup script to ensure postgres starts
RUN echo '#!/bin/bash\nservice postgresql start\n/usr/sbin/sshd -D' > /usr/local/bin/vde-start.sh && \
    chmod +x /usr/local/bin/vde-start.sh

CMD ["/usr/local/bin/vde-start.sh"]
