# VDE ARCHITECTURAL RECORD
# @forge (Governance Sentinel)
@core-infrastructure @embed-spoke
Feature: The Embed Spoke
  Embedded development is a toolchain family, not a language. A Foundling
  flashing an ESP32 with esptool, writing firmware in C against
  arm-none-eabi-gcc, and driving a harness in Rust should not need three
  Spokes with three disjoint tool sets.

  The embed Spoke carries that family for all four languages. It is also the
  intended future home for the USB debug-probe grant, which cannot be narrowed
  to one device and so must not be spread across the general-purpose Spokes.
  That grant is NOT made here: this Spoke receives serial access only, and
  nothing on USB major 189.

  # ---------------------------------------------------------------------------
  # Registry: no Docker, no hardware.
  # ---------------------------------------------------------------------------

  @config @embed-registry
  Scenario: The Vault carries a conforming embed entry
    Given the VDE registry is loaded
    Then the registry must contain a Spoke named "vde-embed"
    And the Spoke "vde-embed" must resolve from the alias "embed"
    And the Spoke "vde-embed" must resolve from the alias "embedded"
    And the Spoke "vde-embed" must hold SSH port 2224
    And the Spoke "vde-embed" must hydrate from "scripts/setup/embed-init.zsh"
    And every registry entry must carry exactly 8 fields

  @config @embed-registry
  Scenario: The documented language port range covers the embed Spoke
    Given the VDE registry is loaded
    Then the language SSH port range comment must include port 2224

  @config @embed-usb
  Scenario: The embed Spoke is opted into USB serial access
    Given the VDE registry is loaded
    Then a USB overlay must exist for the Spoke "embed"
    And the USB overlay for "embed" must declare the service "vde-embed"
    And the USB overlay for "embed" must not grant any wildcard device rule

  # ---------------------------------------------------------------------------
  # Toolchain: requires the built image.
  # ---------------------------------------------------------------------------

  @integration @embed-toolchain
  Scenario Outline: The embedded toolchain is present and executable
    Given the image for Spoke "embed" has been built
    And the Spoke "embed" is running
    Then the command "<tool>" must be available in Spoke "embed"

    Examples:
      | tool              |
      | arm-none-eabi-gcc |
      | gdb-multiarch     |
      | clang             |
      | ld.lld            |
      | openocd           |
      | st-flash          |
      | st-info           |
      | dfu-util          |
      | avrdude           |
      | esptool           |
      | probe-rs          |
      | picocom           |
      | cargo             |
      | clangd            |
      | lldb              |
      | clang-tidy        |
      | clang-format      |
      | llvm-objcopy      |
      | llvm-size         |
      | g++               |
      | cmake             |
      | cargo-size        |
      | cargo-objdump     |

  @integration @embed-toolchain
  Scenario Outline: Rust bare-metal targets are installed
    Given the image for Spoke "embed" has been built
    And the Spoke "embed" is running
    Then the Rust target "<target>" must be installed in Spoke "embed"

    Examples:
      | target                      |
      | thumbv7em-none-eabihf       |
      | thumbv7m-none-eabi          |
      | thumbv6m-none-eabi          |
      | riscv32imc-unknown-none-elf |

  @integration @embed-toolchain
  Scenario: Python serial support is importable
    Given the image for Spoke "embed" has been built
    And the Spoke "embed" is running
    Then the Python module "serial" must import in Spoke "embed"

  @integration @embed-toolchain
  Scenario: The embed Spoke can cross-compile for the STM32F303
    Given the image for Spoke "embed" has been built
    And the Spoke "embed" is running
    When the dev user cross-compiles a bare-metal object for "thumbv7em-none-eabihf" in Spoke "embed"
    Then the compile must succeed
    And the produced object must be ARM 32-bit ELF

  # ---------------------------------------------------------------------------
  # Inherited capability from Signets #526 and #528.
  # ---------------------------------------------------------------------------

  @integration @embed-usb
  Scenario: The embed Spoke inherits serial slots and per-port names
    Given the image for Spoke "embed" has been built
    And the Spoke "embed" is running
    Then the Spoke "embed" must report device cgroup rule "c 188:0 rmw"
    And the Spoke "embed" must not report any wildcard device cgroup rule
    And the Spoke "embed" must not be privileged
    And the node "/dev/ttyUSB0" in Spoke "embed" must be group "devuser" with mode "660"
    And the directory "/dev/vde/by-port" must exist in Spoke "embed"
