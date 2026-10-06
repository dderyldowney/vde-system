# Hub-side USB rules (host, not Spoke)

These install on the **Hub** (the Docker host), not into an image. They are
versioned here so the USB serial overlay has a reproducible host-side half.

| File | Installs to | Purpose |
| --- | --- | --- |
| `99-vde-usb.rules` | `/etc/udev/rules.d/` | hub autosuspend, ModemManager ignore, per-board symlinks, port-name remap |
| `vde-usb-remap` | `/usr/local/bin/` (0755) | re-points `/dev/vde/by-port/*` on a plug event |

## Install

```zsh
sudo install -m 0755 configs/udev/vde-usb-remap /usr/local/bin/vde-usb-remap
sudo install -m 0644 configs/udev/99-vde-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=usb --action=change
```

## Verify

```zsh
ls -l /dev/esp32 /dev/mega2560 /dev/stlink-vcp      # per-board names (if attached)
cat /sys/bus/usb/devices/1-3/power/runtime_status   # active
udevadm info -q property -n /dev/ttyUSB0 | grep ID_MM_DEVICE_IGNORE   # 1
vde usb-map rust                                    # names resolve
journalctl -t vde-usb-remap -n 5                    # "remapped vde-rust" per plug
```

## Notes

- The vendor/product IDs are specific to this Hub's dock (VIA Labs `2109:2817`
  and `2109:0817`) and a CP210x board (`10c4:ea60`). Add your own IDs from
  `lsusb` for other hardware; a CH340 line (`1a86:7523`) is included already.
- Section 3 of the rules file adds automation the guide declines
  ("There is no background watcher by design"). It is event-driven, not a
  watcher: udev fires it once per kernel event, with no sleep and no poll loop,
  so it is consistent with the NO SLEEP mandate (AGENTS.md). Drop that one line
  if the manual `vde usb-map <spoke>` refresh is preferred.
- `power/control` reverts to `auto` on reboot without these rules installed.
- Section 2b gives each board a fixed HOST-side name keyed on its bridge chip's
  vid:pid, so a flash command never has to name a moving ttyUSB<#>. Only the
  CP2102 (esp32) pair is hardware-verified; the CH340 (mega2560) and ST-LINK
  entries are from spec. Inside a Spoke use `/dev/vde/by-port/<port>` instead --
  containers get no udev events and never see these symlinks.

See `docs/guides/usb-serial-boards.md` for the Spoke-side design.
