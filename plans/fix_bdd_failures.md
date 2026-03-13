# Remediation Plan: BDD Test Failures

## Step 1: Environmental Hygiene & State Reset (High 1 & Medium 2)
**Goal:** Ensure the testing environment is clean before scenarios run, preventing "poisoned" states and `[ORPHANED]` VM errors.
- **Action 1.1:** Inspect `tests/features/environment.py` and test utilities.
- **Action 1.2:** Enhance the `before_all` or `before_scenario` hooks to ensure all VDE containers are stopped and orphaned states are cleared. 
- **Action 1.3:** Verify the `ORPHANED` issue goes away for the "how do I connect to Python?" scenario.

## Step 2: Natural Language Parsing for "stop everything" (High 2)
**Goal:** Fix the intent parser so "stop everything" translates to `stop_vm`.
- **Action 2.1:** Inspect `lib/vde-parser` and `tests/features/steps/documented_workflow_steps.py`.
- **Action 2.2:** Add regex/keyword mapping for "stop everything", "stop all", etc.
- **Action 2.3:** Verify intent mapping passes.

## Step 3: Port Auto-Allocation Logic (Medium 1)
**Goal:** Instead of blindly incrementing a port by 1 on conflict (e.g., 2213 -> 2214), VDE should find the *highest* assigned port across all VMs and allocate `max + 1`.
- **Action 3.1:** Locate the port allocation logic (likely in `lib/vm-common` or `bin/add-vm-type`).
- **Action 3.2:** Modify the algorithm to scan `vm-types.json` or `vm-types.conf`, find the maximum used port in the target range (2200-2299), and assign `max + 1`.
- **Action 3.3:** Update the BDD test assertions to match this new, safer logic.

## Step 4: Fix `remove-virtual` Directory Preservation (Low 1)
**Goal:** The `remove-virtual` command should destroy the container and perhaps the `.env` file, but it must preserve the `docker-compose.yml` for easy recreation.
- **Action 4.1:** Read `bin/remove-virtual`.
- **Action 4.2:** Identify the deletion logic (`rm -rf ...`).
- **Action 4.3:** Change it so it removes the `.env` file and stops the container, but explicitly leaves the `configs/docker/<vm>/docker-compose.yml` file intact.

## Step 5: `vde-net` Non-Instantiation (Medium 3)
**Goal:** Fix the issue where `vde-net` does not exist or fails validation in `vm_docker_network_steps.py:56`.
- **Action 5.1:** Check how and when `vde-net` is instantiated (usually via `bin/start-virtual` or `vde-init`).
- **Action 5.2:** Ensure the test or the core logic correctly creates the docker network if it's missing before bringing up the VMs.

## Step 6: Rebuild Workflows and Timeouts (High 3)
**Goal:** Fix the rebuild timeout and verify the rebuilt VM correctly starts.
- **Action 6.1:** Inspect the BDD rebuild tests.
- **Action 6.2:** Increase timeouts to accommodate Docker build times (or cache appropriately) in `docker_lifecycle_steps.py`.
- **Action 6.3:** Micromanage a rebuild test run to ensure no underlying errors are being masked by the timeout.