# language: en
Feature: Productivity Features for Developers
  As a developer
  I want shortcuts and automation for common tasks
  So that I can focus on coding instead of environment management

  Scenario: One command to start entire project stack
    Given my project needs python, postgres, and redis
    When I run "start-virtual python postgres redis"
    Then all three VMs should start with one command
    And I don't need to remember separate commands for each

  Scenario: Start all my project VMs by name
    Given I have 5 VMs configured for my project
    When I run "start-virtual all"
    Then all my created VMs should start
    And I don't need to list each one individually

  Scenario: Quick access to my projects via SSH
    Given I have VMs running for my project
    When I run "ssh python-dev"
    Then I should be connected immediately
    And I don't need to remember ports or IP addresses
    And SSH agent forwarding is automatic

  Scenario: Access code from host editor
    Given my VM is running with volume mounts
    When I edit files in projects/<lang>/ on my host
    Then changes are immediately visible in the VM
    And I can use my preferred editor (VSCode, vim, etc.)
    And I don't need to edit files inside the container

  Scenario: Run commands on host from within VM
    Given I'm working inside a VM
    When I want to run a command on my host
    Then I can use the host communication tools
    And I don't need to exit the VM

  Scenario: Share a single PostgreSQL across projects
    Given I have multiple projects using PostgreSQL
    When I start one postgres VM
    And I start multiple language VMs
    Then all language VMs can connect to the same postgres
    And I don't need separate databases for each project

  Scenario: Use my host's Git credentials from VM
    Given I'm working inside a VM
    When I need to git push to GitHub
    Then SSH agent forwarding gives me access to my keys
    And I don't need to copy keys into the container
    And I can push without entering passwords

  Scenario: Persistent data survives container restart
    Given I have data in postgres
    When I stop and restart postgres VM
    Then my data should still be there
    And I don't lose work between sessions

  Scenario: Quick project switching
    Given I'm working on a Python project
    When I want to switch to a Rust project
    And I run "ssh rust-dev"
    Then I'm immediately in the Rust environment
    And I don't need to change terminal or context manually

  Scenario: Consistent tool versions across team
    Given my project requires specific Node version
    When the team defines the JS VM with that version
    Then everyone gets the same Node version
    And "works on my machine" problems are reduced

  Scenario: Develop with database like in production
    Given production uses PostgreSQL with specific extensions
    When I configure the postgres VM with those extensions
    Then my local database matches production
    And I catch compatibility issues early

  Scenario: Run services in background while I work
    Given I need postgres and redis running
    When I start them as service VMs
    Then they run in background
    And I can focus on my application VM
    And they stay running across coding sessions

  Scenario: Test with clean state quickly
    Given I need to test with fresh database
    When I stop and remove postgres
    And I recreate and start it
    Then I get a fresh database instantly
    And I don't need to manually clean data

  Scenario: Develop offline if needed
    Given I'm working without internet
    When my Docker images are already built
    Then I can start and use VMs offline
    And I'm not blocked by network issues

  Scenario: Extend VM with custom packages
    Given I need additional tools in my Python VM
    When I modify the Dockerfile to add packages
    And I rebuild with --rebuild
    Then the packages are available in the VM
    And I don't need to manually install each time

  Scenario: View all running VMs at a glance
    Given I have multiple VMs running
    When I run "docker ps"
    Then I can see all my VDE containers
    And I can verify what's currently active

  Scenario: Clean stop of all VMs
    Given I'm done working for the day
    When I run "shutdown-virtual all"
    Then all VMs stop gracefully
    And no orphaned containers remain
    And my system is clean

  Scenario: Development environment survives reboot
    Given I've configured my VMs
    When I restart my computer
    And I run "start-virtual all" again
    Then all my VMs start with saved configuration
    And I don't need to reconfigure anything

  Scenario: Run tests in isolated environment
    Given I need to run tests that might modify system state
    When I run tests inside a VM
    Then my host system is not affected
    And I can run destructive tests safely
    And I can discard and recreate VM if needed

  Scenario: Hot reload during development
    Given I'm developing a web application
    And I have a watcher/reloader configured
    When I edit code in my editor on host
    Then the application inside VM detects the change
    And it hot-reloads automatically
    And I see changes without manual restart

  Scenario: Debug across multiple services
    Given I have a web app (python), database (postgres), and cache (redis)
    When I need to debug an issue
    Then I can SSH into each service independently
    And I can check logs for each service
    And I can trace requests across services

  Scenario: Development database with seed data
    Given I need realistic data for development
    When I create a seed script and run it in postgres VM
    Then the data persists across VM restarts
    And I always have a fresh starting point
    And I can reset data when needed

  Scenario: Multiple Node.js versions side by side
    Given project A needs Node 16
    And project B needs Node 18
    When I create js-node16 VM and js-node18 VM
    Then each VM has its own Node version
    And I can work on both projects simultaneously
    And versions don't conflict

  Scenario: Parallel development on microservices
    Given I'm working on a microservices architecture
    When I start all service VMs (auth, api, worker, frontend)
    Then all services can run simultaneously
    And they can communicate via internal network
    And I can test the entire system locally

  Scenario: Quick prototyping with new language
    Given I want to try out a new language
    When I create a VM for that language
    Then I can experiment immediately
    And I can delete the VM if I don't want it
    And my main development environment is untouched

  Scenario: Pair programming with shared VM
    Given I'm pairing with a colleague
    When we both SSH into the same VM
    Then we can work on the same code
    And we can see each other's changes
    And we can use tmux or similar for shared terminal

  Scenario: VSCode Remote-SSH development
    Given I have VMs running
    When I open VSCode and connect to python-dev via Remote-SSH
    Then I get full IDE experience inside the VM
    And I can use VSCode extensions for Python
    And I can debug directly from my editor

  Scenario: Run background workers in dedicated VM
    Given my app has background job processing
    When I create a dedicated worker VM
    Then worker runs independently of web VM
    And I can scale workers separately
    And I can restart worker without affecting web

  Scenario: Development SSL/TLS setup
    Given I need to test HTTPS locally
    When I configure nginx VM with SSL
    Then I can access my app over HTTPS locally
    And certificates can be self-signed for development
    And browser warnings are expected but acceptable

  Scenario: Database migrations across environments
    Given I have migration scripts
    When I run migrations in development VM
    Then I can test migrations safely
    And I can verify schema changes work
    And production database is not affected

  Scenario: API mocking and stubbing
    Given I'm developing a client that calls external APIs
    When I create a mock service VM
    Then I can mock API responses
    And I can test error conditions
    And I don't need to hit real external services

  Scenario: Log aggregation for debugging
    Given multiple VMs generate logs
    When I check logs for each VM
    Then I can view logs from docker logs command
    Or I can check logs/<vm>/ directories
    And I can trace issues across services

  Scenario: File watching and rebuilds
    Given I'm compiling code inside VM
    When source files change on host
    Then the VM sees the changes immediately
    And my build tool can rebuild automatically
    And I don't need to manually trigger builds

  Scenario: Database backups and restores
    Given I have important data in postgres VM
    When I create a backup of data/postgres/
    Then I can restore from backup later
    And I can migrate data to another machine
    And my work is safely backed up

  Scenario: Performance testing with realistic load
    Given I need to test performance
    When I start multiple instances of my service VM
    Then I can generate realistic load
    And I can identify bottlenecks
    And I don't need external infrastructure

  Scenario: Development vs production configuration
    Given I have different settings for dev and production
    When I use environment variables
    Then development uses dev settings
    And production VM can use production settings
    And I don't mix up configurations

  Scenario: Clean workspace for each project
    Given I work on multiple unrelated projects
    When each project has its own VM
    Then dependencies don't conflict between projects
    And I can switch contexts cleanly
    And each project has isolated workspace

  Scenario: Automated testing workflow
    Given I have a comprehensive test suite
    When I push code changes
    Then CI runs tests in similar VMs
    And local test results match CI results
    And I catch issues before pushing

  Scenario: Quick code review setup
    Given a colleague wants to review my code
    When I share the repository
    And they create the same VMs I have
    Then they can run my code immediately
    And they see the same environment I do
    And review process is faster

  Scenario: Development secrets management
    Given my app needs API keys and secrets
    When I use env-files for secrets
    Then secrets are not committed to git
    And each developer has their own env file
    And production secrets are never in development

  Scenario: Weekend project - quick start Monday
    Given I worked on a project Friday
    When I come back Monday
    And I run "start-virtual all"
    Then my entire environment is ready
    And I can continue exactly where I left off
    And no setup is needed

  Scenario: Learning a new framework with sandbox
    Given I want to learn Django/FastAPI/etc.
    When I create a dedicated VM for learning
    Then I can experiment freely
    And I can break things without consequences
    And I can delete the VM when done learning
