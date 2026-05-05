<div align="center">

# ⚡ AIOS
### Autonomous Intelligent Operating System

*A bare-metal OS with a local LLM as its core intelligence engine*

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](./LICENSE)
[![Phase](https://img.shields.io/badge/phase-2%20%E2%80%94%20Core%20Systems-brightgreen.svg)](#roadmap-progress)
[![Architecture](https://img.shields.io/badge/arch-x86__64-blue.svg)](#)
[![Language](https://img.shields.io/badge/language-C%20%2F%20Assembly-orange.svg)](#)

</div>

---

## Vision

> Build a bare-metal Operating System from scratch that runs a local LLM as its core logic engine — eliminating reliance on external APIs and creating a truly **autonomous, intelligent computer system**.

AIOS is not an OS that runs AI applications. AIOS *is* the AI. The kernel, scheduler, memory manager, and shell are all designed around a single goal: running a local language model directly on bare hardware with no userland dependencies.

---

## Roadmap Progress

| Phase | Name | Deliverable | Version | Status |
|-------|------|-------------|---------|--------|
| 1 | Foundation | Bootloader + Long Mode + Kernel | v0.1.0 | ✅ Complete |
| 2 | Core Systems | Memory Manager + Interrupts + Keyboard | v0.2.0 | ✅ Complete |
| 3 | Storage | File System + Disk Drivers | v0.3.0 | 🔄 Next |
| 4 | Multitasking | Scheduler + User Mode + Syscalls | v0.5.0 | ⬜ |
| 5 | AI Layer | AVX Math + Transformer + Local Inference | v0.8.0 | ⬜ |
| 6 | Interaction | GUI + NLP Shell | v1.0.0 | ⬜ |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  NLP Shell (Phase 6)             │
│        "Open file X" → LLM → sys_open("X")       │
├─────────────────────────────────────────────────┤
│              Local LLM Engine (Phase 5)          │
│   Tokenizer │ Transformer │ AVX2 MatMul │ GGUF   │
├─────────────────────────────────────────────────┤
│           Multitasking + Scheduler (Phase 4)     │
│     PCB │ Context Switch │ AI-Priority Queue     │
├─────────────────────────────────────────────────┤
│              File System (Phase 3)               │
│         FAT32 │ VFS │ Tensor Partition Format    │
├─────────────────────────────────────────────────┤
│          Core Kernel Systems (Phase 2) ✅         │
│   PMM │ VMM │ kmalloc │ Keyboard │ PIT │ PCI     │
├─────────────────────────────────────────────────┤
│            Foundation — Phase 1 ✅               │
│   Multiboot2 │ GDT │ IDT │ VGA │ PIC Remap       │
└─────────────────────────────────────────────────┘
              x86_64 Bare Metal Hardware
```

---

## What's Built (Phase 2 — v0.2.0) ✅

### 2.1 — Memory Management

| File | Description |
|------|-------------|
| `pmm.c` / `pmm.h` | Physical Memory Manager — bitmap allocator, Multiboot2 memory map parsing, 1M frame support |
| `vmm.c` / `vmm.h` | Virtual Memory Manager — 4-level paging (PML4), `map`/`unmap`/`virt_to_phys`, TLB flush |
| `heap.c` / `heap.h` | Kernel heap — `kmalloc` / `kfree` with free-list allocator |
| `pmm_alloc_contiguous()` | **AIOS Tensor Allocator** — allocates contiguous physical pages for matrix operations |

### 2.2 — Interrupts & Hardware

| File | Description |
|------|-------------|
| `idt.c` / `isr_stubs.asm` | Full IDT (256 gates), PIC remapped, ISR stubs |
| `keyboard.c` / `keyboard.h` | PS/2 keyboard driver — scan code → ASCII, shift/caps support |
| `pit.c` / `pit.h` | PIT (Programmable Interval Timer) — system clock at configurable Hz |
| `apic.c` / `apic.h` | **AIOS APIC** — Advanced PIC setup for multi-core SMP (parallel AI tasks) |

### 2.3 — Basic Drivers

| File | Description |
|------|-------------|
| `pci.c` / `pci.h` | PCI bus enumeration — scans all devices, reads vendor/class IDs |
| `ahci.h` | AHCI SATA disk driver header — disk sector read/write interface |
| `serial.c` / `serial.h` | Serial port (COM1) driver — kernel debug logging without screen |

---

## What's Built (Phase 1 — v0.1.0)

### `boot/`
- **`kernel_entry.asm`** — Multiboot2 header, 16 KiB stack, calls `kernel_main`
- **`linker.ld`** — Linker script: kernel loaded at 1 MiB physical
- **`grub.cfg`** — GRUB2 boot menu

### `kernel/`
| File | Description |
|------|-------------|
| `kernel_main.c` | Entry point — initializes GDT, IDT, prints banner |
| `vga.c` / `vga.h` | Full VGA text driver (80×25, 16 colors, hardware cursor, scroll) |
| `gdt.c` / `gdt.h` | GDT with null / kernel-code / kernel-data / user segments |
| `idt.c` / `idt.h` | IDT (256 gates), PIC remapped to `INT 0x20–0x2F`, panic screen |
| `isr_stubs.asm` | 256 NASM-generated ISR stubs + pointer table |

---

## Quick Start

### Prerequisites

```bash
# Ubuntu / WSL2 (recommended)
sudo apt install nasm qemu-system-x86 grub-pc-bin xorriso mtools build-essential

# You must build a cross-compiler:
# https://wiki.osdev.org/GCC_Cross-Compiler
# Target: x86_64-elf-gcc
```

### Build & Run

```bash
git clone https://github.com/hillaryns/AIOS..git
cd AIOS.

# Install system deps
./build.sh deps

# Build ISO + launch in QEMU
./build.sh run

# Debug with GDB
./build.sh debug

# Build ISO only
./build.sh iso

# Clean artifacts
./build.sh clean
```

### Expected Output (Phase 2 — v0.2.0)

```
======================================================
   AIOS — Autonomous Intelligent Operating System
   Phase 2: Core Kernel Systems
======================================================

  [ OK ] Multiboot2 handoff verified
  [ OK ] GDT loaded (null / kernel-code / kernel-data / user-code / user-data)
  [ OK ] IDT loaded, PIC remapped (IRQ0-15 → INT 0x20-0x2F)
  [ OK ] STI — interrupts enabled
  [ OK ] PMM initialised — 126 MB free
  [ OK ] VMM initialised (4-level paging active)
  [ OK ] Heap initialised
  [ OK ] PIT configured — 1000 Hz system clock
  [ OK ] Keyboard driver active
  [ OK ] APIC initialised (SMP ready)
  [ OK ] PCI bus enumerated
  [ OK ] Serial port (COM1) active

  AIOS Initialized — Phase 2 Complete. Ready for Phase 3 (Storage & Filesystem).
```

---

## Repository Structure

```
AIOS/
├── README.md
├── LICENSE
├── Makefile                    ← x86_64-elf cross-compiler build system
├── build.sh                    ← Quick-start: deps / run / debug / clean
├── ROADMAP/
│   ├── ⚡ AIOS — Development Roadmap.md
│   └── 🚀 AIOS: From Zero to Execution.md
├── boot/
│   ├── kernel_entry.asm        ← Multiboot2 + stack + kernel_main call
│   ├── linker.ld               ← Memory layout (kernel @ 1 MiB)
│   └── grub.cfg                ← GRUB2 config
├── kernel/
│   ├── kernel_main.c           ← Kernel entry point
│   ├── vga.c / vga.h           ← VGA text driver
│   ├── gdt.c / gdt.h           ← Global Descriptor Table
│   ├── idt.c / idt.h           ← Interrupt Descriptor Table
│   ├── isr_stubs.asm           ← 256 ISR stubs
│   ├── pmm.c / pmm.h           ← Physical Memory Manager (bitmap)
│   ├── vmm.c / vmm.h           ← Virtual Memory Manager (4-level paging)
│   ├── heap.c / heap.h         ← Kernel heap (kmalloc/kfree)
│   ├── keyboard.c / keyboard.h ← PS/2 keyboard driver
│   ├── pit.c / pit.h           ← Programmable Interval Timer
│   ├── apic.c / apic.h         ← Advanced PIC (SMP support)
│   ├── pci.c / pci.h           ← PCI bus enumeration
│   ├── ahci.h                  ← AHCI SATA disk driver
│   ├── serial.c / serial.h     ← Serial port (COM1) logging
│   └── include/
└── docs/
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Assembly | NASM (Intel syntax, ELF64) |
| Kernel language | C (freestanding, `-ffreestanding -mno-red-zone`) |
| Cross-compiler | `x86_64-elf-gcc` (GCC/Binutils) |
| Boot protocol | Multiboot2 (GRUB2) |
| Emulator | QEMU (`qemu-system-x86_64`) |
| Debugger | GDB with QEMU remote stub |
| Target | x86_64 bare metal |

---

## Contributing

This repository is **proprietary**. Contributions are limited to authorized maintainers only. See [`LICENSE`](./LICENSE) for full terms.

If you are an authorized maintainer:
1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit with conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`
4. Open a Pull Request targeting `hillaryns/AIOS.`

---

## Maintainers

| Name | GitHub |
|------|--------|
| Hillary | [@hillaryns](https://github.com/hillaryns) |
| Subhobhai | [@subhobhai943](https://github.com/subhobhai943) |
| Subham | [@SUBHAM646](https://github.com/SUBHAM646) |

---

## License

Copyright © 2026 AIOS Maintainers (Hillary NS, Subhobhai Sarkar, Subham). All rights reserved.

This software is proprietary and confidential. See [`LICENSE`](./LICENSE) for full terms. Unauthorized use, reproduction, or distribution is strictly prohibited.
