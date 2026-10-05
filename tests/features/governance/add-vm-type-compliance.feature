# VDE ARCHITECTURAL RECORD
# @forge (Governance Sentinel)
@governance @add-vm-type @vault-mutating
Feature: The Canonical VM Type Tool Produces Compliant Artifacts
  bin/add-vm-type is the documented way to register a VM type. Whatever it
  forges must satisfy the same mandates the Forge enforces on hand-written
  artifacts, or the canonical path leaves the repository failing its own Rule
  Spine.

  This was not caught for a long time because every existing hydration ritual
  was hand-written with a correct tag afterwards. Nothing tested the tool's
  OUTPUT.

  Each scenario registers a throwaway type. The Vault, the live SSH config and
  the allocated port are backed up and restored around EACH scenario, so a
  failure part-way through a registration cannot leave residue behind.

  @spec @positioning-law
  Scenario: A forged hydration ritual satisfies the Positioning Law
    Given the VDE registry is loaded
    When I register the throwaway VM type "spinecheck" through the canonical entrypoint
    Then the command should succeed
    And a hydration ritual must exist for "spinecheck"
    And the hydration ritual for "spinecheck" must carry an architectural tag on line 2 or 3

  @spec @rule-spine
  Scenario: The Forge still passes its own Rule Spine after a registration
    Given the VDE registry is loaded
    When I register the throwaway VM type "spinecheck" through the canonical entrypoint
    Then the command should succeed
    And the Sovereign Audit must return PASS

  @spec @beskar-vault
  Scenario: A forged registry entry matches the layout of its siblings
    Given the VDE registry is loaded
    When I register the throwaway VM type "spinecheck" through the canonical entrypoint
    Then the command should succeed
    And the registry entry for "spinecheck" must carry exactly 8 fields
    And the registry entry for "spinecheck" must use the placeholder for every empty field
    And the registry entry for "spinecheck" must list "spinecheck" among its aliases
    And the registry entry for "spinecheck" must sit inside the language block

  @spec @usp
  Scenario: A forged hydration ritual satisfies Universal Script Parity
    Given the VDE registry is loaded
    When I register the throwaway VM type "spinecheck" through the canonical entrypoint
    Then the command should succeed
    And the hydration ritual for "spinecheck" must declare "set -e"
    And the hydration ritual for "spinecheck" must declare "export DEBIAN_FRONTEND=noninteractive"
    And the hydration ritual for "spinecheck" must purge apt ghosts
    And the hydration ritual for "spinecheck" must carry the Forged in Beskar header

  @spec @round-trip
  Scenario: Registration is fully reversible across both SSH configs
    Given the VDE registry is loaded
    When I register the throwaway VM type "roundtrip" through the canonical entrypoint
    Then the command should succeed
    And both SSH configs must carry a host block for "roundtrip"
    When I remove the throwaway VM type "roundtrip" through the canonical entrypoint
    Then the command should succeed
    And neither SSH config must carry a host block for "roundtrip"
    And the registry must no longer contain "roundtrip"

  @spec @port-ranges
  Scenario: A service type is allocated a port its own schema accepts
    Given the VDE registry is loaded
    When I register the throwaway service type "svcproof" on service port 9998
    Then the command should succeed
    And the registry entry for "svcproof" must hold an SSH port inside the service range
    And the registry must satisfy its own schema
    When I remove the throwaway VM type "svcproof" through the canonical entrypoint
    Then the command should succeed
    And the registry must no longer contain "svcproof"

  @spec @port-ranges @error-path
  Scenario: An out-of-range SSH port is refused rather than written
    Given the VDE registry is loaded
    When I try to register the service type "svcbad" on SSH port 2226
    Then the command should fail
    And the registry must no longer contain "svcbad"
    And the registry must satisfy its own schema
