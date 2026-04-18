@system-spine
Feature: SSH Configuration Version Alignment
  As an Alor of the VDE
  I require the SSH configuration to match the Sovereign Baseline
  So that the Forge remains synchronized

  Scenario: Verify SSH Configuration Version
    Given the Hub is synchronized to version 1.4.1
    Then the file "configs/ssh/config" should contain "Sovereign Baseline: 1.4.1"
