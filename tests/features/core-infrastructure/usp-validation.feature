Feature: Universal Script Parity (USP) Validation
  @usp @critical-path @usp-hardening
  Scenario: Verify all registered VMs have compliant setup scripts
    Given the VDE registry is loaded
    Then every VM must have a setup script in scripts/setup/
    And every script must have 'set -e' for deterministic error handling
    And every script must have 'apt-get clean' to minimize image size
    And every script must have 'rm -rf /var/lib/apt/lists/*' to purge ghosts
