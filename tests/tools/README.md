# tests/tools
<!-- @forge (Governance Sentinel) -->

Hand-run diagnostics for hardware the automated suites cannot assume is
attached. Not invoked by behave or pytest.

| Tool | Purpose |
| --- | --- |
| `esp-probe` | Reset an ESP32 over DTR/RTS and capture its boot banner |

## esp-probe

```zsh
esp-probe [port] [seconds]
```

Port defaults to `/dev/esp32` (the udev symlink from `configs/udev/`), else the
first `/dev/ttyUSB*`. **Inside a Spoke, pass the stable per-port name** instead,
since a container sees no udev symlinks:

```zsh
vde enter rust
python3 /vde/tests/tools/esp-probe /dev/vde/by-port/1-3.1
```

`/vde` is the read-only Hub mount every Spoke carries, so the script is already
present in a Spoke without copying it in.

Stdlib only -- no pyserial -- so it runs unchanged in any Spoke that has
python3. It opens the port with `O_NOCTTY`, so unplugging the board yields
`ENXIO`/`EIO` rather than `SIGHUP`-killing the process; a plain shell redirect
(`exec 3<>/dev/ttyUSB0`) does get killed, which is worth knowing when writing
your own serial code.

Exit codes: `0` bytes captured, `1` none (board idle or absent), `2` open
failed.

Verified 2026-10-06 against an ELEGOO ESP32 (CP2102, `10c4:ea60`): captured the
full boot banner on the Hub and from inside `vde-rust`, across unplug, replug,
and a 13-second power cycle with the port held open.
