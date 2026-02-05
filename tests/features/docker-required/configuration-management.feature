# language: en
@wip
@user-guide-internal
@wip
@requires-docker-host
Feature: Configuration Management
  # SKIPPED: Configuration management tests need VDE implementation updates - deferring to Phase 3
  As a developer
  I want to configure VDE to match my project needs
  So that my development environment matches my requirements

  Scenario: Configure VM with custom install command
    Given I need specific packages in my Python VM
    When I add a VM type with custom install command
    Then "apt-get install -y python3 python3-pip my-package" should run
    And my custom packages should be available in the VM

  Scenario: Add service VM with custom port
    Given I need a MySQL service on port 3306
    When I run "add-vm-type --type service --svc-port 3306 mysql 'apt-get install -y mysql-server'"
    Then mysql VM should be created
    And port 3306 should be mapped to host
    And I can connect to MySQL from other VMs

  Scenario: Configure VM with multiple service ports
    Given I need a service that exposes multiple ports
    When the VM type configuration includes multiple ports
    Then all ports should be mapped in docker-compose.yml
    And each port should be accessible from host
    And each port should be accessible from other VMs

  Scenario: Set display name for VM
    Given I want friendly names in listings
    When I add VM type with --display "Go Language"
    Then "Go Language" should appear in list-vms output
    And the display name should be used in all user-facing messages

  Scenario: Configure aliases for VM
    Given I want to reference VMs with short names
    When I add VM type with aliases "js,node,nodejs"
    Then I can use any alias to reference the VM
    And "start-virtual js", "start-virtual node", "start-virtual nodejs" all work
    And aliases should show in list-vms output

  Scenario: Override default port ranges
    Given I need different port ranges for my environment
    When I modify VDE_LANG_PORT_START and VDE_LANG_PORT_END
    Then new VMs should use ports in my custom range
    And existing VMs keep their allocated ports

  Scenario: Configure custom Docker base image
    Given I need a different base OS or variant
    When I modify base-dev.Dockerfile
    And I rebuild VMs with --rebuild
    Then VMs should use my custom base image
    And my OS-specific requirements should be met

  Scenario: Configure environment variables for VM
    Given my application needs specific environment variables
    When I create env-files/myapp.env
    And I add variables like NODE_ENV=development
    Then variables should be available in the VM
    And variables are loaded automatically when VM starts

  Scenario: Configure custom UID/GID for container user
    Given my host user has different UID/GID than 1000
    When I modify the UID and GID in docker-compose.yml
    Then container user should match my host user
    And file permissions should work correctly
    And I won't have permission issues on shared volumes

  Scenario: Configure volume mounts for VM
    Given I need to mount specific directories into the VM
    When I modify the volumes section in docker-compose.yml
    Then my custom directories should be mounted
    And files should be shared between host and VM
    And changes should sync immediately

  Scenario: Configure container resource limits
    Given I want to limit VM memory usage
    When I add mem_limit to docker-compose.yml
    Then container should be limited to specified memory
    And container should not exceed the limit
    And my system stays responsive

  Scenario: Configure DNS resolution for VMs
    Given I need custom DNS for my VMs
    When I modify DNS settings in docker-compose.yml
    Then VMs should use my DNS servers
    And name resolution should work as configured

  Scenario: Configure network for VM isolation
    Given I need some VMs on isolated networks
    When I create custom networks in docker-compose.yml
    Then VMs can be isolated as needed
    And specific VMs can communicate
    And other VMs cannot reach isolated VMs

  Scenario: Configure log output for VM
    Given I want to control VM logging
    When I modify logging configuration in docker-compose.yml
    Then logs can go to files, syslog, or stdout
    And log rotation can be configured
    And I can control log verbosity

  Scenario: Configure restart policy
    Given I want VMs to restart automatically
    When I set restart: always in docker-compose.yml
    Then VM restarts if it crashes
    And VM starts on system boot (if Docker does)
    And my environment recovers automatically

  Scenario: Configure health check for VM
    Given I want to know if VM is healthy
    When I add healthcheck to docker-compose.yml
    Then Docker monitors VM health
    And I can see health status in docker ps
    And unhealthy VMs can be restarted automatically

  Scenario: Share configuration across team
    Given I want team to use same VM configuration
    When I commit docker-compose.yml and env-files to git
    Then team members get identical configuration
    And environment is consistent across team
    And "works on my machine" is reduced

  Scenario: Local-only configuration overrides
    Given I need local configuration different from team
    When I create .env.local or docker-compose.override.yml
    And I add it to .gitignore
    Then my local overrides are not committed
    And team configuration is not affected
    And I can customize for my environment

  Scenario: Configure multiple instances of same VM type
    Given I need two different Python environments
    When I create "python-dev" and "python-test" VMs
    Then both should use python base configuration
    But each should have separate data directory
    And each can run independently

  Scenario: Validate configuration before use
    Given I've modified VM configuration
    When I run validation or try to start VM
    Then syntax errors should be caught
    And invalid ports should be rejected
    And missing required fields should be reported

  Scenario: Migrate configuration after VDE update
    Given VDE configuration format has changed
    When I pull the latest VDE
    Then old configurations should still work
    And migration should happen automatically
    And I should be told about manual steps if needed

  Scenario: Reset configuration to defaults
    Given I've made configuration changes I want to undo
    When I remove my custom configurations
    And I reload VM types
    Then default configurations should be used
    And my VMs work with standard settings

  Scenario: Debug configuration issues
    Given my VM won't start due to configuration
    When I check docker-compose config
    Then I should see the effective configuration
    And errors should be clearly indicated
    And I can identify the problematic setting
