# language: en
@user-guide-internal
@requires-docker-host
Feature: Docker Operations
  As a developer
  I want reliable Docker Compose operations with error handling
  So that VM containers start and stop correctly

  Scenario: Build Docker image for VM
    Given VM "python" docker-compose.yml exists
    When I start VM "python"
    Then docker-compose build should be executed
    And image should be built successfully

  Scenario: Start container with docker-compose up
    Given VM "python" image exists
    When I start VM "python"
    Then docker-compose up -d should be executed
    And container should be running

  Scenario: Stop container with docker-compose down
    Given VM "python" is running
    When I stop VM "python"
    Then docker-compose down should be executed
    And container should not be running

  Scenario: Restart container
    Given VM "python" is running
    When I restart VM "python"
    Then container should be stopped
    And container should be started
    And container should have new container ID

  Scenario: Rebuild with --build flag
    Given VM "python" is running
    When I start VM "python" with --rebuild
    Then docker-compose up --build should be executed
    And image should be rebuilt

  Scenario: Rebuild without cache with --no-cache flag
    Given VM "python" is running
    When I start VM "python" with --rebuild and --no-cache
    Then docker-compose up --build --no-cache should be executed

  Scenario: Handle port allocation errors
    Given all ports in range are in use
    When I create a new VM
    Then error should indicate "No available ports"
    And VM should not be created

  Scenario: Handle Docker daemon not running
    Given Docker daemon is not running
    When I try to start a VM
    Then error should indicate "Cannot connect to Docker daemon"
    And command should fail gracefully

  Scenario: Handle network errors
    Given dev-network does not exist
    When I start a VM
    Then network should be created automatically
    And error should indicate network issue

  Scenario: Handle image pull failures
    Given image does not exist locally
    And registry is not accessible
    When I start a VM
    Then error should indicate image pull failure
    And container should not start

  Scenario: Parse Docker error messages
    Given docker-compose operation fails
    When stderr is parsed
    Then "port is already allocated" should map to port conflict error
    And "network.*not found" should map to network error
    And "permission denied" should map to permission error

  Scenario: Retry transient failures with exponential backoff
    Given docker-compose operation fails with transient error
    When operation is retried
    Then retry should use exponential backoff
    And maximum retries should not exceed 3
    And delay should be capped at 30 seconds

  Scenario: Handle disk space errors
    Given no disk space is available
    When I try to start a VM
    Then error should indicate "no space left on device"
    And command should fail immediately

  Scenario: Get container status
    Given VM "python" exists
    When I check VM status
    Then status should be one of: "running", "stopped", "not_created", "unknown"

  Scenario: Detect running containers
    Given multiple VMs are running
    When I get running VMs
    Then all running containers should be listed
    And stopped containers should not be listed

  Scenario: Use correct docker-compose project name
    Given VM "python" is started
    Then docker-compose project should be "vde-python"

  Scenario: Container naming follows convention
    Given language VM "python" is started
    Then container should be named "python-dev"
    Given service VM "postgres" is started
    Then container should be named "postgres"

  Scenario: Volume mounts are created correctly
    Given VM "python" is started
    Then projects/python volume should be mounted
    And logs/python volume should be mounted
    And volume should be mounted from host directory

  Scenario: Environment variables are passed to container
    Given VM "python" has env file
    When container is started
    Then env file should be read by docker-compose
    And SSH_PORT variable should be available in container
