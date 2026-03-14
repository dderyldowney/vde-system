# language: en
@core-infrastructure
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
    When I render the language template with NAME="testlang" SSH_PORT="2250"
    Then the rendered output should contain "vde-testlang"
    And the rendered output should contain "2250"
    And the rendered output should NOT contain "{{NAME}}"
    And the rendered output should NOT contain "{{SSH_PORT}}"

  Scenario: Render service VM template
    Given service template exists at "templates/compose-service.yml"
    And template contains "{{SERVICE_PORT}}" placeholder
    When I render the service template with NAME="testsvc" SSH_PORT="2450" SERVICE_PORT="5432"
    Then the rendered output should contain "5432:5432" port mapping

  Scenario: Template includes SSH agent forwarding
    Given language VM template is rendered
    Then the rendered output should contain SSH_AUTH_SOCK mapping
    And the rendered output should contain .ssh volume mount

  Scenario: Template includes public keys volume
    Given language VM template is rendered
    Then the rendered output should contain public-ssh-keys volume
    And the volume should be mounted at /public-ssh-keys

  Scenario: Template uses correct network
    Given any VM template is rendered
    Then the rendered output should contain "vde-net" network

  Scenario: Template sets correct restart policy
    Given any VM template is rendered
    Then the rendered output should contain "restart: unless-stopped"

  Scenario: Template configures user correctly
    Given language VM template is rendered
    Then the rendered output should contain "devuser"
    And the rendered output should specify UID and GID as "1000"

  Scenario: Template exposes SSH port
    Given any VM template is rendered
    Then the rendered output should expose port "22"
    And the rendered output should map SSH port to host port

  Scenario: Template includes install command
    Given VM "python" has install command "apt-get install -y python3"
    When the template is rendered
    Then the rendered output should include the install command

  Scenario: Handle missing template gracefully
    Given template file does not exist
    When I try to render the template
    Then error should indicate "Template not found"
