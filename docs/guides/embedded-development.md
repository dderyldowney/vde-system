# Embedded Development
<!-- @armor (Engine Core) -->

The **embed** Spoke: one environment carrying the embedded toolchain family for
Python, C, C++ and Rust in the **Sovereign Baseline**.

[← Back to README](../../README.md)

## Why this Spoke exists

Embedded work is a toolchain family, not a language. Flashing an ESP32 with
`esptool`, writing its firmware in C against `arm-none-eabi-gcc`, and driving a
test harness in Rust are three parts of one job. Doing them in three separate
Spokes means three disjoint tool sets and no single place where a board, a
compiler and a debugger meet.

`embed` is that place.

## Getting in

```zsh
vde create embed      # first time
vde start embed
vde enter embed
```

Aliases `embed` and `embedded` both work.

## What is installed

Everything is baked at image build time. There is no runtime `apt`, no runtime
download — the Spoke is **Born Ready**.

### C and C++

| Tool | Purpose |
|---|---|
| `gcc`, `g++`, `cmake`, `make` | native builds |
| `arm-none-eabi-gcc` | bare-metal ARM cross-compiler |
| `binutils-arm-none-eabi` | `arm-none-eabi-objcopy`, `readelf`, `size` |
| `libnewlib-arm-none-eabi` | bare-metal C library |
| `gdb-multiarch` | cross-architecture debugger |

Debian removed `gdb-arm-none-eabi`; `gdb-multiarch` replaces it and speaks ARM.

### The LLVM suite

| Tool | Purpose |
|---|---|
| `clang`, `clang++` | LLVM C/C++ compiler |
| `ld.lld` | LLVM linker |
| `clangd` | language server, for editor integration |
| `lldb` | LLVM debugger |
| `clang-tidy`, `clang-format` | linting and formatting |
| `clang-tools` | `scan-build` and friends |
| `llvm-objcopy`, `llvm-size`, `llvm-nm`, `llvm-objdump` | LLVM binutils |
| `libclang-dev`, `llvm-dev` | headers for building against LLVM |
| `libc++-dev`, `libc++abi-dev` | LLVM C++ standard library |

### Rust

Installed via `rustup`, with bare-metal targets:

| Target | Parts |
|---|---|
| `thumbv7em-none-eabihf` | Cortex-M4F — STM32F303 |
| `thumbv7m-none-eabi` | Cortex-M3 |
| `thumbv6m-none-eabi` | Cortex-M0 / M0+ |
| `riscv32imc-unknown-none-elf` | ESP32-C3 |

Plus the Rust side of LLVM: the `llvm-tools` component and `cargo-binutils`,
which expose `cargo size`, `cargo objdump` and `cargo nm` for inspecting
firmware and converting an ELF into a `.bin` or `.hex`.

### Python

`python3`, `pyserial` (importable as `serial`), `pyusb`, and `esptool` in an
isolated `pipx` venv. Debian 12 enforces PEP 668, so `esptool` is deliberately
**not** installed into the system interpreter.

### Flashing and debugging

| Tool | Use |
|---|---|
| `esptool` | ESP32 / ESP8266 over serial |
| `avrdude` | AVR, including the Mega 2560 |
| `openocd` | SWD / JTAG, broad target support |
| `probe-rs` | modern SWD / JTAG, Rust-native |
| `st-flash`, `st-info` | ST-LINK, from `stlink-tools` |
| `dfu-util` | USB DFU bootloaders |
| `picocom`, `minicom`, `screen` | serial terminals |

## Serial boards

`embed` is opted into USB serial passthrough, so it carries the same twelve
slots and per-port names as the `python`, `rust`, `c` and `cpp` Spokes:

```zsh
ls -l /dev/ttyUSB* /dev/ttyACM*
vde usb-map embed
```

See [USB Serial Boards](usb-serial-boards.md) for the full mechanism, hotplug
behaviour and troubleshooting.

## Cross-compiling for the STM32F303

C, freestanding:

```zsh
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
  -ffreestanding -nostdlib -O2 -c firmware.c -o firmware.o
arm-none-eabi-readelf -h firmware.o      # ELF32, ARM, relocatable
```

Rust:

```zsh
cargo build --release --target thumbv7em-none-eabihf
cargo size --release --target thumbv7em-none-eabihf
cargo objcopy --release --target thumbv7em-none-eabihf -- -O binary firmware.bin
```

## Debug probes

The flashing and debugging **tools** are installed, but a Spoke is not yet
granted access to a USB debug probe. Probes sit on USB major 189, a grant that
cannot be narrowed to a single device, so it is deliberately withheld pending
its own Strike — and when it lands it will be scoped to this Spoke alone rather
than spread across the general-purpose language Spokes.

Until then, serial flashing works fully: `esptool` for ESP32 parts and
`avrdude` for AVR both run over `/dev/ttyUSB*` and `/dev/ttyACM*`.

## Related

- [USB Serial Boards](usb-serial-boards.md)
- [Getting Started](getting-started.md)
