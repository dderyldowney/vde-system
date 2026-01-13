Feature: Docker and Container Management
  As a developer using VDE
  I want VDE to handle Docker container complexity
  So I can focus on development without managing containers

  Scenario: Automatic Docker network creation
    Given I start my first VM
    Then VDE should create the dev-net network
    And all VMs should join this network
    And VMs should be able to communicate by name

  Scenario: Port allocation for SSH
    Given I create multiple VMs
    When each VM starts
    Then each should get a unique SSH port
    And ports should be auto-allocated from available range
    And no two VMs should have the same SSH port

  Scenario: Service port configuration
    Given I create a PostgreSQL VM
    When it starts
    Then the PostgreSQL port should be mapped
    And I can connect to PostgreSQL from the host
    And other VMs can connect using the service name

  Scenario: Volume mounts for workspace
    Given I start any VM
    Then my workspace directory should be mounted
    And files I create are visible on the host
    And changes persist across container restarts

  Scenario: Data persistence for services
    Given I create a PostgreSQL VM
    When I stop and restart PostgreSQL
    Then my data should be preserved
    And databases should remain intact
    And I should not lose any data

  Scenario: Container resource limits
    Given I have multiple running VMs
    When I check resource usage
    Then each container should have reasonable limits
    And no single VM should monopolize resources
    And the system should remain responsive

  Scenario: Container health monitoring
    Given I have running VMs
    When I query VM status
    Then I should see which containers are healthy
    And I should see any that are failing
    And I should be able to identify issues

  Scenario: Cleaning up stopped containers
    Given I have stopped several VMs
    When I start them again
    Then old containers should be removed
    And new containers should be created
    And no stopped containers should accumulate

  Scenario: Docker Compose integration
    Given VDE creates a VM
    Then a docker-compose.yml file should be generated
    And I can manually use docker-compose if needed
    And the file should follow best practices

  Scenario: Multi-stage build optimization
    Given I rebuild a language VM
    Then the build should use multi-stage Dockerfile
    And final images should be smaller
    And build cache should be used when possible

  Scenario: Container startup order
    Given I have dependent services
    When I start them together
    Then they should start in a reasonable order
    And dependencies should be available when needed
    And the startup should complete successfully

  Scenario: Container isolation
    Given I have multiple VMs running
    When one VM crashes
    Then other VMs should continue running
    And the crash should not affect other containers
    And I can restart the crashed VM independently

  Scenario: Container logs
    Given I have a running VM
    When I need to debug an issue
    Then I can view the container logs
    And logs should show container activity
    And I can troubleshoot problems
