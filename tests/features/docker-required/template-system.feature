# language: en
@user-guide-internal
@requires-docker-host
Feature: Template System
  As a developer
  I want VM configurations to be generated from templates
  So that new VMs can be created consistently

  Scenario: Render language VM template
    Given language template exists at "templates/compose-language.yml"
    And template contains "{{NAME}}" placeholder
    And template contains "{{SSH_PORT}}" placeholder
    When I render template with NAME="go" and SSH_PORT="2202"
    Then rendered output should contain "go"
    And rendered output should contain "2202"
    And rendered output should NOT contain "{{NAME}}"
    And rendered output should NOT contain "{{SSH_PORT}}"

  Scenario: Render service VM template
    Given service template exists at "templates/compose-service.yml"
    And template contains "{{SERVICE_PORT}}" placeholder
    When I render template with NAME="redis" and SERVICE_PORT="6379"
    Then rendered output should contain "6379:6379" port mapping

  Scenario: Handle multiple service ports
    Given service VM has multiple ports "8080,8081"
    When template is rendered
    Then rendered output should contain "8080:8080"
    And rendered output should contain "8081:8081"

  Scenario: Escape special characters in template values
    Given template value contains special characters
    When I render template with value containing "/" or "&"
    Then special characters should be properly escaped
    And rendered template should be valid YAML

  Scenario: Template includes SSH agent forwarding
    Given language VM template is rendered
    Then rendered output should contain SSH_AUTH_SOCK mapping
    And rendered output should contain .ssh volume mount

  Scenario: Template includes public keys volume
    Given language VM template is rendered
    Then rendered output should contain public-ssh-keys volume
    And volume should be mounted at /public-ssh-keys

  Scenario: Template uses correct network
    Given any VM template is rendered
    Then rendered output should contain "vde-network" network

  Scenario: Template sets correct restart policy
    Given any VM template is rendered
    Then rendered output should contain "restart: unless-stopped"

  Scenario: Template configures user correctly
    Given language VM template is rendered
    Then rendered output should contain "user: devuser"
    And rendered output should specify UID and GID as "1000"

  Scenario: Template exposes SSH port
    Given any VM template is rendered
    Then rendered output should expose port "22"
    And rendered output should map SSH port to host port

  Scenario: Template includes install command
    Given VM "python" has install command "apt-get install -y python3"
    When template is rendered
    Then rendered output should include the install command

  Scenario: Handle missing template gracefully
    Given template file does not exist
    When I try to render the template
    Then error should indicate "Template not found"
