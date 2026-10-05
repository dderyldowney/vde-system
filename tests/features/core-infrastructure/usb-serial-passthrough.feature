# VDE ARCHITECTURAL RECORD
# @forge (Governance Sentinel)
@core-infrastructure @usb-serial
Feature: USB Serial Board Passthrough
  Foundlings and Reinforcements in the embedded-devices field plug development
  boards into the Hub and must reach them from inside their Spoke. Boards surface
  on the Hub as /dev/ttyUSB<n> (usb-serial, major 188) or /dev/ttyACM<n>
  (cdc-acm, major 166).

  The Spoke is granted scoped device cgroup rules through an opt-in overlay, and
  the entrypoint pre-creates the device nodes at every start. A Spoke stays
  healthy with no board attached, and a replug needs no restart and no
  host-side watcher.

  # ---------------------------------------------------------------------------
  # Fast scenarios: config generation only, no Docker, no hardware.
  # ---------------------------------------------------------------------------

  @config @usb-opt-in
  Scenario: Only the embedded-capable Spokes receive the USB overlay
    Given the VDE registry is loaded
    Then a USB overlay must exist for the Spoke "python"
    And a USB overlay must exist for the Spoke "rust"
    And a USB overlay must exist for the Spoke "c"
    And a USB overlay must exist for the Spoke "cpp"
    And a USB overlay must exist for the Spoke "embed"
    And no USB overlay must exist for the Spoke "go"

  @config @usb-opt-in
  Scenario Outline: The overlay grants serial majors and nothing wider
    Given the VDE registry is loaded
    Then the USB overlay for "<spoke>" must declare the service "vde-<spoke>"
    And the USB overlay for "<spoke>" must grant the device cgroup rule "c 188:0 rmw"
    And the USB overlay for "<spoke>" must grant the device cgroup rule "c 188:7 rmw"
    And the USB overlay for "<spoke>" must grant the device cgroup rule "c 166:0 rmw"
    And the USB overlay for "<spoke>" must grant the device cgroup rule "c 166:3 rmw"
    And the USB overlay for "<spoke>" must not grant any wildcard device rule
    And the USB overlay for "<spoke>" must grant exactly one rule per declared node
    And the USB overlay for "<spoke>" must not grant any rule for USB bus major 189
    And the USB overlay for "<spoke>" must not enable privileged mode
    And the USB overlay for "<spoke>" must not declare any "devices:" mapping
    And the USB overlay for "<spoke>" must declare the node spec "ttyUSB:188:8 ttyACM:166:4"

    Examples:
      | spoke  |
      | python |
      | rust   |
      | c      |
      | cpp    |
      | embed  |

  @config @usb-compose-selection
  Scenario: Compose invocations include the overlay only where it exists
    Given the VDE registry is loaded
    Then the compose file list for "python" must include the base compose file
    And the compose file list for "python" must include the USB overlay
    And the base compose file must come first in the compose file list for "python"
    And the compose file list for "go" must contain only the base compose file

  # ---------------------------------------------------------------------------
  # Integration scenarios: require Docker, require NO hardware.
  # ---------------------------------------------------------------------------

  @integration @usb-runtime @no-board
  Scenario: A Spoke ignites and stays healthy with no board attached
    Given no USB serial board is attached to the Hub
    When I execute "bin/vde start python"
    Then the command should succeed
    And the Spoke "python" should be running

  @integration @usb-runtime
  Scenario: The running Spoke carries scoped rules and no privilege
    Given the Spoke "python" is running
    Then the Spoke "python" must report device cgroup rule "c 188:0 rmw"
    And the Spoke "python" must report device cgroup rule "c 188:7 rmw"
    And the Spoke "python" must report device cgroup rule "c 166:0 rmw"
    And the Spoke "python" must report device cgroup rule "c 166:3 rmw"
    And the Spoke "python" must not report any wildcard device cgroup rule
    And the Spoke "python" must not be privileged

  @integration @usb-runtime
  Scenario Outline: Serial nodes are pre-created and owned by the dev group
    Given the Spoke "python" is running
    Then the node "<node>" in Spoke "python" must have major "<major>" and minor "<minor>"
    And the node "<node>" in Spoke "python" must be group "devuser" with mode "660"

    Examples:
      | node         | major | minor |
      | /dev/ttyUSB0 | 188   | 0     |
      | /dev/ttyUSB7 | 188   | 7     |
      | /dev/ttyACM0 | 166   | 0     |
      | /dev/ttyACM3 | 166   | 3     |

  @integration @usb-runtime @error-path
  Scenario: An empty slot fails fast and leaves the Spoke healthy
    Given the Spoke "python" is running
    And the node "/dev/ttyUSB7" in Spoke "python" has no board behind it
    When the dev user opens "/dev/ttyUSB7" in Spoke "python"
    Then the open must fail with errno 6 for ENXIO
    And the open must not block for longer than 5 seconds
    And the Spoke "python" should be running

  @integration @usb-runtime @security
  Scenario: The serial grant does not reach the USB bus
    Given the Spoke "python" is running
    When the dev user opens a fabricated node for major 189 in Spoke "python"
    Then the open must fail with errno 1 for EPERM

  @integration @usb-runtime
  Scenario: A Spoke without the overlay has no serial access
    When I execute "bin/vde start go"
    Then the command should succeed
    And the Spoke "go" must report no device cgroup rule for major 188
    And the node "/dev/ttyUSB0" must not exist in Spoke "go"

  # ---------------------------------------------------------------------------
  # Hardware-in-the-loop: require a real board. Skipped loudly when absent.
  # These must never pass without exercising real hardware.
  # ---------------------------------------------------------------------------

  @hardware @usb-serial-hw
  Scenario: A board attached before ignition is readable in the Spoke
    Given a USB serial board is attached to the Hub
    And the Spoke "python" is running
    When the dev user opens the attached board node in Spoke "python"
    Then the open must succeed
    And the serial driver must answer a termios query

  @usb-serial-hw @hardware-interactive @no-board
  Scenario: A board plugged in while the Spoke runs needs no restart
    Given the Spoke "python" is running
    And no USB serial board is attached to the Hub
    When a USB serial board is plugged into the Hub
    Then the dev user must be able to open the attached board node in Spoke "python"
    And the Spoke "python" must not have been restarted

  @hardware @usb-serial-hw @hardware-interactive
  Scenario: Unplugging the board fails cleanly without a restart
    Given the Spoke "python" is running
    And a USB serial board is attached to the Hub
    When the board is unplugged from the Hub
    Then the open must fail with a device-absent errno
    And the Spoke "python" should be running

  @hardware @usb-serial-hw @hardware-interactive
  Scenario: A replug is reachable without recreating the node
    Given the Spoke "python" is running
    And a USB serial board has been unplugged and replugged
    When the dev user opens the attached board node in Spoke "python"
    Then the open must succeed
    And the node must not have been recreated

  @hardware @usb-serial-hw @hardware-interactive
  Scenario: A replug while the port is held open lands on a spare slot
    Given the Spoke "python" is running
    And the dev user is holding the board node open in Spoke "python"
    When the board is unplugged and replugged while the port is held
    Then the board must surface on the next minor
    And the dev user must be able to open that spare node in Spoke "python"
