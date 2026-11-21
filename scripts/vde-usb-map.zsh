#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USB Port Map - stable per-port names for serial boards (Signet #528).
#
# Runs INSIDE a Spoke. Baked into vde-base, so every Spoke carries it, but it
# is inert unless VDE_USB_TTY_NODES is set (the USB overlay from Signet #526).
#
# WHY: identical USB-serial bridges report identical serial strings, so
# /dev/serial/by-id collides and cannot distinguish two boards of the same
# model. ttyUSB<n> is assigned by enumeration order, not by socket. The USB
# PORT PATH (e.g. "1-3.3" = bus 1, hub port 3, downstream port 3) is a
# property of where the cable is plugged, so it is stable across replugs.
#
# HOW: sysfs is visible inside a container even though udev is not.
#   /sys/class/tty/ttyUSB1 -> .../usb1/1-3/1-3.3/1-3.3:1.0/ttyUSB1/tty/ttyUSB1
#                                            ^^^^^ the port path
# Everything from the ":interface" component onward is stripped to reach the
# USB device directory, which carries idVendor, idProduct and serial.
#
# LIMITATION: a container receives no udev events, so the symlink set is
# accurate as of the last run. Re-run after plugging a board in:
#   vde usb-map <spoke>
# No poll loop is used; the NO SLEEP mandate forbids it and a watcher was
# already proven unnecessary for the device nodes themselves in Signet #526.

emulate -L zsh
setopt extended_glob

typeset -g VDE_USB_SYSFS_CLASS="${VDE_USB_SYSFS_CLASS:-/sys/class/tty}"
typeset -g VDE_USB_MAP_DIR="${VDE_USB_MAP_DIR:-/dev/vde/by-port}"

# _usb_map_root_exec - run a command, escalating only if it is actually needed.
# Attempting unprivileged first avoids a pointless sudo when the target is
# already writable, and keeps the script usable outside a Spoke for testing.
_usb_map_root_exec() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
    return $?
  fi

  if "$@" 2>/dev/null; then
    return 0
  fi

  sudo -n "$@" 2>/dev/null
}

# _usb_map_resolve SYSFS_LINK
# Print "<port_path>\t<device_dir>" for a tty sysfs link, or nothing when the
# link does not sit under a USB device (for example a virtual console).
_usb_map_resolve() {
  local link="${1}"
  local target
  target=$(readlink -f "${link}" 2>/dev/null) || return 1
  [[ -n "${target}" ]] || return 1

  local -a parts
  parts=( ${(s:/:)target} )

  local accumulated="" port_path="" iface_id="" device_dir="" part
  for part in "${parts[@]}"; do
    # The interface component looks like "1-3.3:1.0". The component before the
    # colon is the stable port path, and the path accumulated so far is the
    # USB device directory holding idVendor/idProduct/serial.
    if [[ "${part}" == <->-<->*:<->.<-> ]]; then
      # "1-3.3:1.0" -> port "1-3.3", interface "1.0". The port alone is shared
      # by EVERY interface of a multi-channel device (FT2232, CP2105, an
      # ESP32-S3 exposing CDC plus a second interface), so the interface must
      # be part of the canonical name or one channel silently overwrites the
      # other's symlink.
      port_path="${part%%:*}"
      iface_id="${part#*:}"
      device_dir="${accumulated}"
      break
    fi
    accumulated="${accumulated}/${part}"
  done

  [[ -n "${port_path}" && -n "${device_dir}" ]] || return 1
  print -r -- "${port_path}	${iface_id}	${device_dir}"
}

# _usb_map_attr DEVICE_DIR ATTRIBUTE
# Print a sysfs attribute, or "none" when it is absent or unreadable.
_usb_map_attr() {
  local dir="${1}" attr="${2}"
  if [[ -r "${dir}/${attr}" ]]; then
    local value
    value=$(<"${dir}/${attr}")
    print -r -- "${value:-none}"
  else
    print -r -- "none"
  fi
}

main() {
  if [[ -z "${VDE_USB_TTY_NODES}" ]]; then
    print -r -- "[VDE-USB-MAP] This Spoke has no USB serial overlay; nothing to map."
    return 0
  fi

  if ! _usb_map_root_exec mkdir -p "${VDE_USB_MAP_DIR}" 2>/dev/null; then
    print -r -- "[VDE-USB-MAP] ERROR: could not create ${VDE_USB_MAP_DIR}."
    return 1
  fi

  # Drop stale links first: a board removed from a socket must not leave a
  # name pointing at a node that now belongs to something else.
  local stale
  for stale in "${VDE_USB_MAP_DIR}"/*(N@); do
    _usb_map_root_exec rm -f "${stale}" 2>/dev/null || true
  done

  local -a links
  links=( "${VDE_USB_SYSFS_CLASS}"/ttyUSB*(N) "${VDE_USB_SYSFS_CLASS}"/ttyACM*(N) )

  # Pass 1: gather. The canonical name carries the interface, because the port
  # alone is ambiguous on multi-channel bridges. A short port-only alias is
  # added in pass 2 only when exactly one interface claims that port, so the
  # common single-channel board keeps a tidy name without risking a collision.
  local -a entries
  local -A port_counts
  local link node resolved port_path iface_id device_dir
  for link in "${links[@]}"; do
    node="/dev/${link:t}"
    # A sysfs entry with no /dev node is a host device outside this Spoke's
    # declared slot range; it has no cgroup grant and cannot be opened here.
    [[ -e "${node}" ]] || continue

    resolved=$(_usb_map_resolve "${link}") || continue
    port_path="${${(s:	:)resolved}[1]}"
    iface_id="${${(s:	:)resolved}[2]}"
    device_dir="${${(s:	:)resolved}[3]}"

    entries+=( "${node}	${port_path}	${iface_id}	${device_dir}" )
    (( port_counts[${port_path}]++ ))
  done

  # Pass 2: link and report.
  local -i failures=0 found=0
  local entry vid pid serial canonical short
  for entry in "${entries[@]}"; do
    node="${${(s:	:)entry}[1]}"
    port_path="${${(s:	:)entry}[2]}"
    iface_id="${${(s:	:)entry}[3]}"
    device_dir="${${(s:	:)entry}[4]}"

    vid=$(_usb_map_attr "${device_dir}" idVendor)
    pid=$(_usb_map_attr "${device_dir}" idProduct)
    serial=$(_usb_map_attr "${device_dir}" serial)

    canonical="${VDE_USB_MAP_DIR}/${port_path}:${iface_id}"
    if ! _usb_map_root_exec ln -sfn "${node}" "${canonical}" 2>/dev/null; then
      print -r -- "[VDE-USB-MAP] ERROR: could not link ${canonical}."
      (( failures++ ))
      continue
    fi

    short=""
    if (( port_counts[${port_path}] == 1 )); then
      short="${VDE_USB_MAP_DIR}/${port_path}"
      if ! _usb_map_root_exec ln -sfn "${node}" "${short}" 2>/dev/null; then
        print -r -- "[VDE-USB-MAP] ERROR: could not link ${short}."
        (( failures++ ))
        short=""
      fi
    fi

    print -r -- "node=${node}	port=${port_path}	iface=${iface_id}	name=${short:-${canonical}}	canonical=${canonical}	vid:pid=${vid}:${pid}	serial=${serial}"
    (( found++ ))
  done

  if (( found == 0 && failures == 0 )); then
    print -r -- "[VDE-USB-MAP] No serial boards attached."
  fi

  (( failures == 0 )) || return 1
  return 0
}

main "$@"
