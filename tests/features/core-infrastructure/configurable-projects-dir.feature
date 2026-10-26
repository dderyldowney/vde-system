# VDE ARCHITECTURAL RECORD
# @forge (Governance Sentinel)
@configurable-projects-dir @core-infrastructure
Feature: Configurable Projects Directory (Signet #543)
  As a student of the VDE
  I require my Projects base to live anywhere I control -- even outside the Forge
  So that my per-Spoke workspaces are mine, wherever I keep them

  # SELF-RESTORING: every scenario first snapshots the repo-root .env and the
  # generated configs, and registers an automatic teardown (context.add_cleanup)
  # that restores them -- so a run leaves `git status` identical with no manual
  # intervention, even if a scenario fails mid-way. Temp bases live OUTSIDE the
  # repo under $HOME/.vde-test-projects-* and are cleaned up too.
  Background:
    Given the repo state is snapshotted for restoration

  # B1: the base is persisted to .env as an absolute key and created on disk.
  Scenario: Re-pointing persists an absolute Projects base to .env and creates it
    Given a clean temporary projects base "current"
    And a non-existent temporary projects base "chosen"
    And VDE_PROJECTS_DIR is exported to base "current"
    When I run "vde set-projects-dir" targeting base "chosen"
    Then the projects command should succeed
    And the repo .env should contain the VDE_PROJECTS_DIR key pointing at base "chosen"
    And the projects base "chosen" should exist on disk
    And the projects base "chosen" should be outside the repository

  # B2: generated compose interpolates the exported base -- outside the repo.
  Scenario: Generated compose resolves the rust workspace outside the repository
    Given a clean temporary projects base "external"
    And all configs are regenerated
    And VDE_PROJECTS_DIR is exported to base "external"
    When I render the resolved compose for "rust"
    Then the resolved rust workspace source should be base "external" alias "rust"

  # B3: a real Spoke truly mounts the student-chosen external directory.
  @container-roundtrip
  Scenario: A rust Spoke mounts the student-chosen external base end to end
    Given a clean temporary projects base "roundtrip"
    And all configs are regenerated
    And VDE_PROJECTS_DIR is exported to base "roundtrip"
    When I recreate the "rust" Spoke from this repo
    Then the "rust" Spoke should be running
    When I create a marker file in the "rust" Spoke workspace
    Then the marker should appear on the host at base "roundtrip" alias "rust"

  # B4: re-point moves alias folders old->new and never overwrites collisions.
  Scenario: Re-pointing moves alias folders and skips name collisions
    Given a clean temporary projects base "old"
    And a clean temporary projects base "new"
    And the projects base "old" has an alias folder "rust" with a marker file
    And the projects base "old" has an alias folder "go" with a marker file
    And the projects base "new" already has an alias folder "go" containing the sentinel "KEEP_ME"
    And VDE_PROJECTS_DIR is exported to base "old"
    When I run "vde set-projects-dir" targeting base "new"
    Then the projects command should succeed
    And the alias folder "rust" and its marker should have moved from base "old" to base "new"
    And the colliding alias "go" should remain in base "old"
    And the sentinel file in base "new" alias "go" should still read "KEEP_ME"
    And the repo .env should contain the VDE_PROJECTS_DIR key pointing at base "new"

  # B5: with the override unset, the in-tree default is unchanged.
  Scenario: With no override the default in-tree projects base is used
    Given all configs are regenerated
    And VDE_PROJECTS_DIR is unset
    Then the projects helper should resolve to the in-tree default
    When I render the resolved compose for "rust"
    Then the resolved rust workspace source should be the in-tree default alias "rust"

  # B6: ADOPTION / NON-DESTRUCTION. A student may point VDE at a directory that
  # already holds their own unrelated work (and even a folder whose name
  # collides with a VDE alias). Creating the per-alias dirs must never overwrite
  # or delete any of it; VDE's alias subfolders coexist alongside it.
  Scenario: Pointing at a pre-populated directory adopts it without clobbering
    Given a clean temporary projects base "adopt"
    And the projects base "adopt" is pre-populated with the student's own work
    And VDE_PROJECTS_DIR is exported to base "adopt"
    When VDE ensures the per-alias directories for "rust,go" under that base
    Then the projects command should succeed
    And the student's pre-existing work in base "adopt" is byte-for-byte intact
    And VDE's new alias folder "go" coexists in base "adopt"
    And the adopted alias folder "rust" still holds the student's own file

  # B7: NUKE DATA INTEGRITY (safe, dry-run only -- never a real nuke here, which
  # would wipe the separate host install's images/network/SSH). Proves nuke
  # reports projects/ and data/ as KEPT and never lists them for removal.
  Scenario: A dry-run nuke keeps projects and data and removes only VDE's own state
    When I run nuke in dry-run mode
    Then the projects command should succeed
    And the dry-run output marks projects and data as KEPT
    And the dry-run output does not list projects or data for removal

  # B8: init --projects-dir PRECEDENCE (flag > exported env > .env).
  # NOTE: the real `vde init` is deliberately NOT exercised end-to-end here --
  # it also runs ssh-setup, builds the base image, installs git hooks and
  # registers clusters, side effects that cannot be byte-restored under the hard
  # isolation mandate. The precedence logic of its resolver
  # (vde_init_resolve_projects_dir, including the --projects-dir flag) is covered
  # as REAL code in tests/unit/vde-init-projects-resolver.test.zsh, which
  # extracts and exercises the live resolver against temp dirs. This note keeps
  # the init-flag gap explicit rather than silent.
