# VDE ARCHITECTURAL RECORD
# @forge (Governance Sentinel)
@core-infrastructure @usb-serial @usb-stable-names
Feature: Stable Per-Port Names For USB Serial Boards
  Signet #526 gave the embedded-capable Spokes access to USB serial boards but
  not the means to tell them apart. Identical bridge chips report identical
  serials, so /dev/serial/by-id entries collide, and ttyUSB<n> is assigned by
  enumeration order rather than by which socket the cable is in.

  A Spoke therefore derives names from the USB PORT PATH, read from sysfs,
  which needs no udev. A board keeps its name across a replug into the same
  socket even when its ttyUSB<n> changes.

  # ---------------------------------------------------------------------------
  # Integration: require Docker, require NO hardware.
  # ---------------------------------------------------------------------------

  @integration @usb-map
  Scenario: The map directory exists in an opted-in Spoke at ignition
    Given the Spoke "python" is running
    Then Spoke "python" must carry the USB map resolver
    And the directory "/dev/vde/by-port" must exist in Spoke "python"

  @integration @usb-map
  Scenario: A Spoke without the USB overlay has no map directory
    When I execute "bin/vde start go"
    Then the command should succeed
    And the directory "/dev/vde/by-port" must not exist in Spoke "go"

  @integration @usb-map
  Scenario: The canonical command succeeds and reports an honest map
    Given the Spoke "python" is running
    When I execute "bin/vde usb-map python"
    Then the command should succeed
    And the map output must list exactly the Spoke's live serial nodes

  @integration @usb-map @error-path @no-board
  Scenario: The map lists nothing when no board is attached
    Given the Spoke "python" is running
    And no USB serial board is attached to the Hub
    When I execute "bin/vde usb-map python"
    Then the command should succeed
    And the map output must list no serial nodes

  # ---------------------------------------------------------------------------
  # Hardware-in-the-loop: require a real board.
  # ---------------------------------------------------------------------------

  @hardware @usb-stable-names-hw
  Scenario: An attached board is reported with its physical port path
    Given a USB serial board is attached to the Hub
    And the Spoke "python" is running
    When I execute "bin/vde usb-map python"
    Then the command should succeed
    And the map output must report the attached board's node
    And the reported port path must match the Hub's own port path for that board

  @hardware @usb-stable-names-hw
  Scenario: The stable name resolves to the real device and opens
    Given a USB serial board is attached to the Hub
    And the Spoke "python" is running
    And the USB map has been refreshed for Spoke "python"
    When the dev user opens the board's stable port name in Spoke "python"
    Then the open must succeed
    And the serial driver must answer a termios query

  @usb-stable-names-hw @hardware-interactive
  Scenario: The stable name survives a replug that moves the node
    Given the Spoke "python" is running
    And a USB serial board is attached to the Hub
    And the USB map has been refreshed for Spoke "python"
    And the dev user is holding the board node open in Spoke "python"
    When the board is unplugged and replugged while the port is held
    And the USB map has been refreshed for Spoke "python"
    Then the board's ttyUSB number must have changed
    And the board's stable port name must be unchanged
    And the dev user must be able to open the board's stable port name in Spoke "python"
