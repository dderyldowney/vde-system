# CouchDB VM Dockerfile
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y curl gnupg && \
    curl https://couchdb.apache.org/repo/keys.asc | gpg --dearmor | tee /usr/share/keyrings/couchdb-archive-keyring.gpg >/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/couchdb-archive-keyring.gpg] https://apache.jfrog.io/artifactory/couchdb-deb/ bookworm main" | tee /etc/apt/sources.list.d/couchdb.list >/dev/null && \
    apt-get update -y && \
    groupadd -r couchdb && useradd -r -g couchdb -m -d /opt/couchdb couchdb && \
    echo "couchdb couchdb/mode select standalone" | debconf-set-selections && \
    echo "couchdb couchdb/bindaddress string 0.0.0.0" | debconf-set-selections && \
    echo "couchdb couchdb/adminpass password password" | debconf-set-selections && \
    echo "couchdb couchdb/adminpass_confirm password password" | debconf-set-selections && \
    (DEBIAN_FRONTEND=noninteractive apt-get install -y couchdb || (rm -f /var/lib/dpkg/info/couchdb.postinst && dpkg --configure -a && apt-get install -f -y)) && \
    mkdir -p /opt/couchdb/etc/local.d /var/log/couchdb /var/lib/couchdb /etc/couchdb && \
    echo "[admins]" > /opt/couchdb/etc/local.d/docker.ini && \
    echo "admin = password" >> /opt/couchdb/etc/local.d/docker.ini && \
    chown -R couchdb:couchdb /opt/couchdb /var/log/couchdb /var/lib/couchdb /etc/couchdb && \
    rm -rf /var/lib/apt/lists/*
