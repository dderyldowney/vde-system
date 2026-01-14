Feature: SSH Agent Forwarding for VM-to-VM Communication
  As a developer working with multiple VMs
  I want to SSH between VMs using my host's SSH keys
  So I don't need to manage separate keys for each VM

  Background:
    Given I have SSH keys configured on my host
    And the SSH agent is running
    And my keys are loaded in the agent

  Scenario: Automatically setting up SSH environment when creating a VM
    Given I do not have an SSH agent running
    And I do not have any SSH keys
    When I create a Python VM
    Then an SSH agent should be started automatically
    And an SSH key should be generated automatically
    And the key should be loaded into the agent
    And no manual configuration should be required

  Scenario: Communicating between language VMs
    Given I have a Go VM running
    And I have a Python VM running
    And I have started the SSH agent
    When I SSH into the Go VM
    And I run "ssh python-dev" from within the Go VM
    Then I should connect to the Python VM
    And I should be authenticated using my host's SSH keys
    And I should not need to enter a password
    And I should not need to copy keys to the Go VM

  Scenario: Communicating between language and service VMs
    Given I have a Python VM running
    And I have a PostgreSQL VM running
    When I SSH into the Python VM
    And I run "ssh postgres-dev" from within the Python VM
    Then I should connect to the PostgreSQL VM
    And I should be able to run psql commands
    And authentication should use my host's SSH keys

  Scenario: Copying files between VMs using SCP
    Given I have a Python VM running
    And I have a Go VM running
    When I create a file in the Python VM
    And I run "scp go-dev:/tmp/file ." from the Python VM
    Then the file should be copied using my host's SSH keys
    And no password should be required

  Scenario: Running commands on remote VMs
    Given I have a Python VM running
    And I have a Rust VM running
    When I run "ssh rust-dev pwd" from the Python VM
    Then the command should execute on the Rust VM
    And the output should be displayed
    And authentication should use my host's SSH keys

  Scenario: Full stack development workflow
    Given I create a Python VM for my API
    And I create a PostgreSQL VM for my database
    And I create a Redis VM for caching
    And I start all VMs
    When I SSH into the Python VM
    And I run "ssh postgres-dev psql -U devuser -l"
    Then I should see the PostgreSQL list of databases
    When I run "ssh redis-dev redis-cli ping"
    Then I should see "PONG"
    And all connections should use my host's SSH keys

  Scenario: Microservices architecture communication
    Given I have a Go VM running as an API gateway
    And I have a Python VM running as a payment service
    And I have a Rust VM running as an analytics service
    When I SSH into the Go VM
    And I run "ssh python-dev curl localhost:8000/health"
    And I run "ssh rust-dev curl localhost:8080/metrics"
    Then both services should respond
    And all authentications should use my host's SSH keys

  Scenario: VM-to-VM SSH in development workflow
    Given I am developing a full-stack application
    And I have frontend, backend, and database VMs
    When I need to test the backend from the frontend VM
    And I run "ssh backend-dev pytest tests/"
    Then the tests should run on the backend VM
    And I should see the results in the frontend VM
    And authentication should be automatic

  Scenario: SSH keys never leave the host
    Given I have SSH keys on my host
    And I have multiple VMs running
    When I SSH from one VM to another
    Then the private keys should remain on the host
    And only the SSH agent socket should be forwarded
    And the VMs should not have copies of my private keys

  Scenario: Multiple VMs can use the same agent
    Given I have 5 VMs running
    And I have 2 SSH keys loaded in the agent
    When I SSH from VM1 to VM2
    And I SSH from VM2 to VM3
    And I SSH from VM3 to VM4
    And I SSH from VM4 to VM5
    Then all connections should succeed
    And all should use my host's SSH keys
    And no keys should be copied to any VM
