Feature: SSH Agent Forwarding for External Git Operations
  As a developer working inside VMs
  I want to use my host's SSH keys for Git operations
  So I can push and pull from GitHub/GitLab without configuring keys in each VM

  Background:
    Given I have SSH keys configured on my host
    And I have a GitHub account with SSH keys configured
    And the SSH agent is running with my keys loaded

  Scenario: Cloning a private repository from within a VM
    Given I have a Python VM running
    And I have a private repository on GitHub
    When I SSH into the Python VM
    And I run "git clone git@github.com:myuser/private-repo.git"
    Then the repository should be cloned
    And I should not be prompted for a password
    And my host's SSH keys should be used for authentication

  Scenario: Pushing code to GitHub from a VM
    Given I have a Go VM running
    And I have cloned a repository in the Go VM
    And I have made changes to the code
    When I run "git commit -am 'Add new feature'"
    And I run "git push origin main"
    Then the changes should be pushed to GitHub
    And my host's SSH keys should be used
    And no password should be required

  Scenario: Pulling from multiple Git hosts
    Given I have a Python VM running
    And I have repositories on both GitHub and GitLab
    And I have SSH keys configured for both hosts
    When I SSH into the Python VM
    And I run "git pull" in the GitHub repository
    And I run "git pull" in the GitLab repository
    Then both repositories should update
    And each should use the appropriate SSH key from my host

  Scenario: Using Git submodules
    Given I have a Rust VM running
    And I have a repository with Git submodules
    And the submodules are from GitHub
    When I SSH into the Rust VM
    And I run "git submodule update --init"
    Then the submodules should be cloned
    And authentication should use my host's SSH keys

  Scenario: Git operations in microservices architecture
    Given I have multiple VMs for different services
    And each service has its own repository
    And all repositories use SSH authentication
    When I SSH to each VM
    And I run "git pull" in each service directory
    Then all repositories should update
    And all should use my host's SSH keys
    And no configuration should be needed in any VM

  Scenario: Deploying code from VM to external server
    Given I have a deployment server
    And I have SSH keys configured for the deployment server
    And I have a Python VM where I build my application
    When I SSH into the Python VM
    And I run "scp app.tar.gz deploy-server:/tmp/"
    And I run "ssh deploy-server '/tmp/deploy.sh'"
    Then the application should be deployed
    And my host's SSH keys should be used for both operations

  Scenario: Multiple GitHub accounts
    Given I have multiple GitHub accounts
    And I have different SSH keys for each account
    And all keys are loaded in my SSH agent
    When I SSH into a VM
    And I clone a repository from account1
    And I clone a repository from account2
    Then both repositories should be cloned
    And each should use the correct SSH key
    And the agent should automatically select the right key

  Scenario: SSH key passed through to child processes
    Given I have a Node.js VM running
    And I have an npm script that runs Git commands
    When I SSH into the Node.js VM
    And I run "npm run deploy" which uses Git internally
    Then the deployment should succeed
    And the Git commands should use my host's SSH keys

  Scenario: Git operations in automated workflows
    Given I have a CI/CD script in a VM
    And the script performs Git operations
    When I run the CI/CD script
    Then all Git operations should succeed
    And my host's SSH keys should be used
    And no manual intervention should be required

  Scenario: No key copying to VMs required
    Given I have a new VM that needs Git access
    And I have SSH keys on my host
    When I create and start the VM
    And I SSH into the VM
    And I run "git clone git@github.com:user/repo.git"
    Then the clone should succeed
    And I should not have copied any keys to the VM
    And only the SSH agent socket should be forwarded
