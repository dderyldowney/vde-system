source lib/vde-shell-compat
source lib/vm-common
source lib/vde-parser
execute_plan <<PLAN
INTENT:connect
VM:vde-python
FLAGS:rebuild=false nocache=false
FILTER:all
PLAN
