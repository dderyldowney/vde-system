# LIFECYCLE OF A SPOKE
<!-- @shared-law (Sovereign Law) -->
**The Lifecycle of a Spoke in the VDE Sovereign Baseline** (1.4.1) is governed by "The Tether" (Proof of Life Contract), a non-negotiable functional sequence that ensures system integrity from initial hydration to final decommissioning.

### **At a Glance: The Spoke Lifecycle**

The lifecycle follows a strictly enforced path: **Init → Create → Start → Enter → Rebuild → Stop → Remove**.

---

### **1\. Ignition: Initialization and Creation**

The lifecycle begins with the environment's readiness and the physical smelting of the Spoke.

* **The Ignition Ritual (vde init)**: This pre-flight phase hydrates the Hub's infrastructure, forging SSH keys, establishing networks, and building the vde-base (Tier 1\) image.  
* **Spoke Creation (vde create \<vm\>)**: A new Spoke is created from the Beskar Registry. This process uses **Universal Script Parity (USP)** to hydrate the environment at build-time, ensuring the Spoke is "Born Ready" (BTO) with no runtime apt requirements.  
* **Dynamic Registration (vde add)**: New Spoke types can be registered dynamically, enforcing an 8-field standard registry structure.

### **2\. Ignition: Active Service**

Once forged, the Spoke enters its functional state.

* **Spoke Ignition (vde start \<vm\>)**: The container process (Tier 3\) is ignited. This includes a "System Breath" resource check and a **Physical Handshake** (Docker Probe) to verify port availability and system readiness.  
* **The Sovereign Handshake (vde enter \<vm\>)**: The user enters the Spoke's login shell via a secure SSH transversal bridge. This bridge utilizes a socat UNIX-listen proxy to forward the host's SSH agent into the Spoke.  
* **Identity Pulse**: The system continuously monitors the active bridge to ensure SSH agent connectivity remains stable within the running container.

### **3\. Maintenance and Re-Forging**

Spokes are designed to be disposable and easily restored.

* **Interaction and Maintenance (vde rebuild \<vm\>)**: If a Spoke becomes unstable or requires updates, it is "Re-forged". This rebuilds the Spoke's Docker image, typically defaulting to a no-cache state to ensure a clean baseline.

### **4\. Decommissioning: The Quench and Dissolution**

The final phase ensures that no "Ghost" processes or artifacts remain on the Hub.

* **The Quench (vde stop \<vm\>)**: The running VM process is quenched (stopped), but the instance remains in the registry.  
* **Dissolution (vde remove \<vm\>)**: The VM instance and its associated atomic file locks are dissolved.  
* **Permanent Removal (vde uninstall \<vm\>)**: The Spoke type is permanently removed from the Registry.  
* **The Great Quench (vde nuke)**: A comprehensive cleanup that removes all VDE artifacts from the Hub.  
* **Tactical Sweep**: A specialized tool used to forcefully purge all vde- containers, clear VM locks, and reset port registries to ensure a pristine environment.

Sources:

* [rewrite-sovereign-artifact-set.md](https://drive.google.com/open?id=1vGDqSzWmyGOF7Kf7n-rcXpTAQh5oHfnH)  
* [vde\_2\_0\_6\_update\_plan.md](https://drive.google.com/open?id=1nf4JDUBwLhj5HaYJBW9N0qAqEdm65djn)  
* [The Tether](https://drive.google.com/open?id=1oI_69s8mY76gfF33fNgNWBYfB1wl_lhq0SFhVJUaqM8)  
* [The Sovereign Baseline (v1.3.1)](https://drive.google.com/open?id=1oBOMr9uU-zNeziyLtw6qFgxegO9xch6VSgb0muyyGaY)  
* [available-scripts.md](https://drive.google.com/open?id=1OpY4e7loh172SVXrmn5M3BGgGKtTBUon)  
* [3-vm-striking-array-update.md](https://drive.google.com/open?id=1_Y4UC33B6aidzsAd3ctTonhrMAoTbbJJ)  
* [ARCHITECTURE.md](https://drive.google.com/open?id=1v_bAHAS6HBWBIqZec_nN-0xY7UunC5RF)  
* [USE\_CASES.md](https://drive.google.com/open?id=1MtZUIDisI1P6VWBjim2XUI8xP1DQmOMh)  
* [FOUNDLING\_GUIDE.md](https://drive.google.com/open?id=1wjoqKmwCWvLkmq7VWhMC83RoscXhP21g)  
* [pristine-environment-implementation.md](https://drive.google.com/open?id=1075ETub4WuWpyaj9j-0j1zqm3856J1a_)  
* [vde-pulse.zsh](https://drive.google.com/open?id=1COR2b9657eSR15gsZ_luF5FG3PoUOuwe)  
* [vde-tactical-sweep.zsh](https://drive.google.com/open?id=1RX3Fzu7-axHAG-EqhTZCidjtQkoA4D4K)