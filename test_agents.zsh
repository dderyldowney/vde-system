#!/usr/bin/env zsh
source ./lib/vde-ssh
echo "First source, Agent PID: ${SSH_AGENT_PID}"
source ./lib/vde-ssh
echo "Second source, Agent PID: ${SSH_AGENT_PID}"
ps -ef | grep ssh-agent | grep vde | grep -v grep
