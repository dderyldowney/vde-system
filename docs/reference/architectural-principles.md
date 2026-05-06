# ARCHITECTURAL PRINCIPLES
<!-- @shared-law (Forge Component) -->
The architectural principles defining the **Sovereign Baseline 1.4.0** are governed by a hierarchical and narrative-driven framework designed for absolute technical integrity and portability. This environment, referred to as the **Forge**, operates under the following core architectural pillars:

### **1\. The Gospel: Sovereign Artifact Set (SAS)**

The SAS is the "synchronized baseline of truth" for the environment. Version 1.4.0 formally expanded this set to **seven authoritative documents** that must be in perfect agreement before any version tag is struck. These documents serve as the definitive "decision-makers" on all system logic and implementation:

1. **docs/governance/vde-spec.md (The Rule of One)**: The absolute authority for versioning and laws.  
2. **USE\_CASES.md (The Creed)**: Defines the "Why" and filters work by educational value for Students (Foundlings) and New Hires (Reinforcements).  
3. **docs/architecture/overview.md (The Skeleton)**: High-level design and structural principles.  
4. **TECHNICAL\_DEEP\_DIVE.md (The Nervous System)**: Granular component logic and workflows.  
5. **VDE\_ANALYSIS.md (The Context)**: Research findings and empirical engineering verdicts.  
6. **PROJECT\_STATUS.md (The Pulse)**: The authoritative record of active system health and state.  
7. **RELEASE\_NOTES.md (The Chronicle)**: Historical record of every Sovereign Baseline release.

### **2\. The Rule Spine: Universal Agent Protocol (UAP)**

The system architecture is strictly enforced by the **UAP**, a sentinel layer (bin/vde-enforce-uap.zsh) that prevents architectural drift.

* **Sovereign ZSH Purity**: All CLI tools, libraries, and shells must use \#\!/usr/bin/env zsh. The use of bash is strictly prohibited and enforced via deep content inspection for native ZSH features.  
* **Zero-Host Dependency (Scavenger's Ban)**: The system must not depend on the tools of the host machine (e.g., avoiding jq in favor of native ZSH parsing). It relies only on the "Unyielding Tetrad": **Zsh, Git, Docker, and SSH**.  
* **Born Ready (BTO)**: Every Spoke (VM) must be fully functional at image creation. Runtime apt calls or network-dependent configurations are prohibited to ensure immutability.

### **3\. Structural Design: Hub-and-Spoke Model**

The 1.4.0 baseline utilizes a three-tier inheritance model:

* **The Hub**: The host machine governing orchestration, security, and global configuration.  
* **The Spoke**: Isolated containers (Jails) where hydration occurs via **Universal Script Parity (USP)**—a mandate that every VM entry points to a specific setup script.  
* **The Transversal Bridge**: A secure SSH-native connection between the Hub and Spokes, bypassing non-standard behaviors of docker exec to mimic production cloud infrastructure.

### **4\. Concurrency & Determinism**

Architectural stability in 1.4.0 is maintained through deterministic state management:

* **Lock-Queue Model**: Competitive spinlocks are replaced with a First-In-First-Out (FIFO) sequencing mechanism using unique ticket files to prevent "Thundering Herd" race conditions during high-volume operations.  
* **Registry Serialization**: All modifications to VM registries and port allocations must occur inside a global configuration lock (global-config.lock).

### **5\. The Release Ritual**

Released in 1.4.0, the **Sovereign Release Law** mandates a strict branch lifecycle:

* **main branch**: The only branch where step tagging (X.X.X) and GitHub releases occur. It represents the immutable Sovereign Baseline.  
* **stable alias**: An automated alias that always points to the current certified main SHA, used for production-ready clones.

### **6\. The Creed-frame Narrative**

Unique to 1.4.0 is the integration of the **Mandalorian and Forge Mythos** as a core architectural mandate. Technical work is not merely code; it is a "strike on the anvil," and all infrastructure must align with this foundational narrative established in data/vde\_core/\*\*.

Would you like me to analyze how these principles are empirically verified by the current test suite?

Sources:

* [2026-04-14-stable-alias-design.md](https://drive.google.com/open?id=1GU6UIGe9AM8Sym09CX7w1HmAOk-zqmGO)  
* [PROJECT\_STATUS.md](https://drive.google.com/open?id=1805zUZKKl2wh7OynkA6MjWG8UdfsLRDT)  
* [vde-enforce-uap.zsh](https://drive.google.com/open?id=1Ny18abPL3GqCkWnss7OIRM0_DYjku7ZM)  
* [forge\_mythos.md](https://drive.google.com/open?id=1VleKjQE5BQQJkjxhI8daWFJwkwkIOeog)  
* [RELEASE\_NOTES.md](https://drive.google.com/open?id=1oVTAUN2zhDazdXuMMMR5q8JQPSDUOGkk)  
* [Technical-Deep-Dive.md](https://drive.google.com/open?id=1_rPjpZKBJMGbnfqoFUXcgTM1gwn8u_Yv)  
* [2026-04-15-sync-sovereign-status.md](https://drive.google.com/open?id=18ays47uJMEE26QrqwJbDt-HoUHWtFtIJ)  
* [The Way](https://drive.google.com/open?id=1LXDfufMSwlgPAHTj1t0Df0dRS1iMGizGAg16AoaVviM)  
* [docs/architecture/overview.md](https://drive.google.com/open?id=1v_bAHAS6HBWBIqZec_nN-0xY7UunC5RF)  
* [docs/governance/vde-spec.md](https://drive.google.com/open?id=1vS5Dj8Pe7Zq2ba2csiKsDvYTQDJKTCgM)  
* [beskar-map.md](https://drive.google.com/open?id=16HNav8fZYAF11n5jQ0-w24Ea5HChkvIj)  
* [vde-security](https://drive.google.com/open?id=1Jj18HQrTEWKJSk6dTTPsIKf28owBN5tG)  
* [VDE\_ANALYSIS.md](https://drive.google.com/open?id=1272F40kI80sPr_MZ9uPkHjpHDc-VeQmz)  
* [The Sovereign Baseline (v1.3.1)](https://drive.google.com/open?id=1oBOMr9uU-zNeziyLtw6qFgxegO9xch6VSgb0muyyGaY)  
* [2026-04-16-finalize-1.4.0.md](https://drive.google.com/open?id=1lyAjTEUyImAUIOh8_6ij5enbcYFIl1-i)  
* [2026-04-15-codify-release-law.md](https://drive.google.com/open?id=1wtWAGzOXWa199Xpdk7XLaVXJPHpiON9H)  
* [vde](https://drive.google.com/open?id=1mw94vCfbMEtWJPv9BB3xeuZErzKz3MMD)  
* [USE\_CASES.md](https://drive.google.com/open?id=1MtZUIDisI1P6VWBjim2XUI8xP1DQmOMh)