# Secure OS diagrams

These diagrams describe this project's actual architecture and experiment boundaries.

## Mission 2: kernel mediation

```mermaid
flowchart LR
    A[Application: syscall_demo] -->|openat / write / close| B[System call boundary]
    B --> K[Guest Linux kernel: validate credentials and arguments]
    K --> F[Filesystem and virtual disk]
```

## Mission 4: address space

```mermaid
flowchart TB
    subgraph A[Process A virtual address space]
      AT[Code: read + execute] --- AD[Data and heap: read + write]
      AD --- AM[Shared libraries / mapped files]
      AM --- AS[Stack: local secret, read + write]
    end
    AS --> PA[Process A page tables]
    subgraph B[Process B virtual address space]
      BS[Same numeric pointer, different mapping or unmapped]
    end
    BS --> PB[Process B page tables]
    PA --> MMU[MMU checks translation and permissions]
    PB --> MMU
    MMU --> RAM[Physical memory pages]
```

Layout is schematic. Actual mappings and permissions come from mission-04/maps.txt; addresses are architecture and run dependent.

## Mission 9: privilege separation

```mermaid
flowchart LR
    U[Untrusted input] --> P[Unprivileged parser]
    P -->|narrow validated request| H[Small privileged helper]
    H --> R[Required protected operation]
    X[Monolithic root application] --> ALL[Many privileged kernel operations]
```

A Linux capability narrows classes of kernel operations; it does not automatically provide a safe request protocol or a secure parser.

## Mission 10: buffer boundary

```text
char buffer[16]: indexes 0..15
+----------------+-----------------+
| 16 valid bytes | adjacent memory |
+----------------+-----------------+
| fixed teaching input: 34 bytes   |
+----------------------------------+
                  ^ out-of-bounds writes begin here
```

A string of 15 bytes plus NUL fits. A string of 16 bytes plus NUL does not. The safe version rejects the latter before copying.

## Missions 16 and 21: actual trust stack

```mermaid
flowchart TB
    C[Container application: separate namespace view]
    A[Guest application]
    C -->|system calls; shared guest kernel| GK[Ubuntu 26.04 ARM64 guest kernel]
    A --> GK
    GK --> VH[Virtual CPU / memory / disk / NAT network]
    VH --> VZ[Apple Virtualization.framework and hypervisor mechanisms]
    VZ --> HK[macOS host kernel]
    HK --> HW[Apple Silicon physical hardware]
    L[Lima: lifecycle and managed SSH transport] --> VZ
```

A container uses the guest kernel; it adds no separate kernel VM boundary. The VM has its own kernel. Lima is the management layer, not itself the hardware hypervisor. Host home directories are not mounted into the guest. No container ports are published. Management SSH forwarding is controlled by Lima and binds on the host loopback interface.
