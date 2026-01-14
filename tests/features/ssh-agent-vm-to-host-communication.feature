Feature: VM-to-Host Communication
  As a developer working inside a VM
  I want to execute commands on my host machine
  So I can integrate VM workflows with host operations

  Background:
    Given I have Docker installed on my host
    And I have VMs running with Docker socket access

  Scenario: Executing commands on host from VM
    Given I have a Python VM running
    And I need to check what's running on my host
    When I SSH into the Python VM
    And I run "to-host docker ps"
    Then I should see a list of running containers
    And the output should show my host's containers

  Scenario: Viewing host logs from VM
    Given I have a Go VM running
    And my host has application logs
    When I SSH into the Go VM
    And I run "to-host tail -f /var/log/app.log"
    Then I should see the host's log output
    And the output should update in real-time

  Scenario: Listing host directories from VM
    Given I have a Python VM running
    And I have projects on my host
    When I SSH into the Python VM
    And I run "to-host ls ~/dev"
    Then I should see a list of my host's directories
    And I should be able to navigate the host filesystem

  Scenario: Checking host resource usage from VM
    Given I have multiple VMs running
    And I need to check resource usage
    When I SSH into a VM
    And I run "to-host docker stats"
    Then I should see resource usage for all containers
    And I should see CPU, memory, and I/O statistics

  Scenario: Managing host containers from VM
    Given I have a management VM running
    And I need to restart a service on my host
    When I SSH into the management VM
    And I run "to-host docker restart postgres"
    Then the PostgreSQL container should restart
    And I should be able to verify the restart

  Scenario: Accessing host files from VM
    Given I have a Python VM running
    And I need to read a configuration file on my host
    When I SSH into the Python VM
    And I run "to-host cat ~/dev/config.yaml"
    Then I should see the contents of the host file
    And I should be able to use the content in the VM

  Scenario: Triggering host builds from VM
    Given I have a build VM running
    And I need to trigger a build on my host
    When I SSH into the build VM
    And I run "to-host cd ~/dev/project && make build"
    Then the build should execute on my host
    And I should see the build output

  Scenario: Coordinating multi-VM operations from host
    Given I have a coordination VM running
    And I need to check the status of other VMs
    When I SSH into the coordination VM
    And I run "to-host docker ps --filter 'name=python-dev'"
    Then I should see the status of the Python VM
    And I can make decisions based on the status

  Scenario: Host backup operations from VM
    Given I have a backup VM running
    And I need to trigger a backup on my host
    When I SSH into the backup VM
    And I run "to-host ~/dev/scripts/backup.sh"
    Then the backup should execute on my host
    And my data should be backed up

  Scenario: Debugging host issues from VM
    Given I have a debugging VM running
    And my host has an issue I need to diagnose
    When I SSH into the debugging VM
    And I run "to-host systemctl status docker"
    Then I should see the Docker service status
    And I can diagnose the issue

  Scenario: Host network operations from VM
    Given I have a network VM running
    And I need to check host network connectivity
    When I SSH into the network VM
    And I run "to-host ping -c 3 github.com"
    Then I should see network connectivity results
    And I can diagnose network issues

  Scenario: Executing custom host scripts from VM
    Given I have a utility VM running
    And I have custom scripts on my host
    When I SSH into the utility VM
    And I run "to-host ~/dev/scripts/cleanup.sh"
    Then the script should execute on my host
    And the cleanup should be performed
