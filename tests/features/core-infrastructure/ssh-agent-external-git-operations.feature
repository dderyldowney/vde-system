# language: en
@parser
Feature: SSH Agent Forwarding Configuration
  As a developer working inside VMs
  I want to use my host's SSH keys for Git operations
  So I can push and pull from GitHub/GitLab without configuring keys in each VM

  @parser
  Scenario: Python VM compose file has SSH agent forwarding configured
    Given VM "python" config exists at "configs/docker/languages/python/docker-compose.yml"
    When I inspect the docker-compose.yml for VM "python"
    Then the compose file should mount the SSH agent socket volume
    And the compose file should set SSH_AUTH_SOCK environment variable

  @parser
  Scenario: Go VM compose file has SSH agent forwarding configured
    Given VM "go" config exists at "configs/docker/languages/go/docker-compose.yml"
    When I inspect the docker-compose.yml for VM "go"
    Then the compose file should mount the SSH agent socket volume
    And the compose file should set SSH_AUTH_SOCK environment variable

  @parser
  Scenario: Rust VM compose file has SSH agent forwarding configured
    Given VM "rust" config exists at "configs/docker/languages/rust/docker-compose.yml"
    When I inspect the docker-compose.yml for VM "rust"
    Then the compose file should mount the SSH agent socket volume
    And the compose file should set SSH_AUTH_SOCK environment variable