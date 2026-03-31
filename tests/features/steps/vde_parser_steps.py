import json
import re
from behave import given, when, then
from vm_common import VDE_ROOT, run_vde_command

# =============================================================================
# UNIQUE STEPS FOR PARSER & DISCOVERY HARDENING
# =============================================================================

# All steps for this feature are currently provided by:
# - documented_workflow_steps.py (Givens)
# - parser_steps.py (Whens/Thens)

# vde_parser_steps.py will remain as a placeholder for FUTURE unique logic
# to avoid AmbiguousStep conflicts with the legacy parser_steps.py.
