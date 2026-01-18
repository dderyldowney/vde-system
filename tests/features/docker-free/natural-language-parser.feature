# language: en
@user-guide-internal
Feature: Natural Language Parser
  As a developer
  I want to control VDE using natural language commands
  So that I don't need to remember specific command syntax

  Scenario: Detect list VMs intent
    When I parse "list all vms"
    Then intent should be "list_vms"

  Scenario: Detect list languages intent
    When I parse "show all language vms"
    Then intent should be "list_vms"
    And filter should be "lang"

  Scenario: Detect list services intent
    When I parse "what services are available"
    Then intent should be "list_vms"
    And filter should be "svc"

  Scenario: Detect create VM intent
    When I parse "create a go vm"
    Then intent should be "create_vm"
    And VMs should include "go"

  Scenario: Detect create multiple VMs intent
    When I parse "create python and rust"
    Then intent should be "create_vm"
    And VMs should include "python"
    And VMs should include "rust"

  Scenario: Detect start VM intent
    When I parse "start the python vm"
    Then intent should be "start_vm"
    And VMs should include "python"

  Scenario: Detect start multiple VMs intent
    When I parse "start python, rust, and go"
    Then intent should be "start_vm"
    And VMs should include "python", "rust", "go"

  Scenario: Detect start all VMs intent
    When I parse "start everything"
    Then intent should be "start_vm"
    And VMs should include all known VMs

  Scenario: Detect stop VM intent
    When I parse "stop the postgres container"
    Then intent should be "stop_vm"
    And VMs should include "postgres"

  Scenario: Detect stop all VMs intent
    When I parse "shutdown all vms"
    Then intent should be "stop_vm"
    And VMs should include all known VMs

  Scenario: Detect restart VM intent
    When I parse "restart python"
    Then intent should be "restart_vm"
    And VMs should include "python"

  Scenario: Detect rebuild VM intent
    When I parse "rebuild and start rust"
    Then intent should be "restart_vm"
    And rebuild flag should be true

  Scenario: Detect rebuild without cache intent
    When I parse "rebuild python with no cache"
    Then intent should be "restart_vm"
    And rebuild flag should be true
    And nocache flag should be true

  Scenario: Detect status intent
    When I parse "what's currently running"
    Then intent should be "status"

  Scenario: Detect status for specific VMs
    When I parse "show status of python and rust"
    Then intent should be "status"
    And VMs should include "python", "rust"

  Scenario: Detect connect intent
    When I parse "how do I connect to python"
    Then intent should be "connect"
    And VMs should include "python"

  Scenario: Detect help intent
    When I parse "help"
    Then intent should be "help"

  Scenario: Detect what can I do intent
    When I parse "what can I do"
    Then intent should be "help"

  Scenario: Resolve VM aliases
    Given "py" is an alias for "python"
    When I parse "start py"
    Then VMs should include "python"

  Scenario: Extract VM names from natural input
    Given known VMs are "python", "rust", "go", "js"
    When I parse "I want to start the python and rust vms"
    Then VMs should include "python", "rust"
    And VMs should NOT include "go", "js"

  Scenario: Handle special characters in input safely
    When I parse "start python; rm -rf /"
    Then dangerous characters should be rejected
    And command should NOT execute

  Scenario: Validate plan lines against whitelist
    Given plan contains "INTENT:start_vm"
    And plan contains "VM:python"
    When plan is validated
    Then all plan lines should be valid
    When plan contains "MALICIOUS:command"
    Then plan should be rejected

  Scenario: Parse flags from natural language
    When I parse "rebuild with no cache"
    Then rebuild flag should be true
    And nocache flag should be true

  Scenario: Handle ambiguous input gracefully
    When I parse "do something with containers"
    Then intent should default to "help"
    And help message should be displayed
