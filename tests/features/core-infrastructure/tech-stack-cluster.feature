@core-infrastructure @tech-stack @cluster @system-spine
Feature: Integrated Tech Stack (Python, PostgreSQL, Redis)
  The VDE provides a pre-verified tech stack for students, ensuring that 
  language VMs and service VMs can be ignited and utilized as a single unit.

  @user-guide-cluster
  Scenario: Verify the Sovereign Tech Stack Cluster
    Given the VDE system is healthy
    When I run the one true way to start the VMs "python postgres redis"
    And I execute "sudo service postgresql start" inside "vde-postgres" as "root"
    And I execute "sudo /usr/bin/redis-server /etc/redis/redis.conf --daemonize yes" inside "vde-redis" as "root"
    Then the container "vde-python" should be started via direct Docker orchestration
    And the container "vde-postgres" should be started via direct Docker orchestration
    And the container "vde-redis" should be started via direct Docker orchestration
    And the VM "vde-postgres" must be responsive on port "5432"
    And the VM "vde-redis" must be responsive on port "6379"
    When I execute "pg_isready -h localhost -p 5432" inside "vde-postgres" as "devuser"
    Then the command execution should succeed
    When I execute "redis-cli ping" inside "vde-redis" as "devuser"
    Then the command execution should succeed
    When I execute "pg_isready -h vde-postgres -p 5432" inside "vde-python" as "devuser"
    Then the command execution should succeed
    And the stack should be gracefully terminated
