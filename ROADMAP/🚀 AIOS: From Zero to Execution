# 🚀 AIOS: From Zero to Execution

---

## Prerequisites: The "Ground Zero" Setup

Before writing a single line of OS code, you must prepare your development environment. You cannot use standard Windows/Linux tools because they assume an OS already exists.

### Action Items

**Set up a Linux Environment:**
Use WSL2 (Windows Subsystem for Linux) or a Linux VM (Ubuntu 22.04 LTS recommended). OS development is significantly harder on native Windows.

**Install Build Tools:**
```bash
sudo apt install build-essential nasm qemu-system-x86 grub-pc-bin xorriso mtools
```
> **Purpose:** `nasm` (assembler), `qemu` (emulator to test your OS), `gcc` (compiler).

**Build a Cross-Compiler (The Hardest First Step):**
- **Why:** Your system `gcc` targets your host OS (Linux/Windows). You need a compiler that targets "Bare Metal" (no OS).
- **Action:** Follow the "GCC Cross-Compiler" guide on OSDev Wiki. Build `x86_64-elf-gcc`.
- **Goal:** You must be able to run `x86_64-elf-gcc --version` successfully.

---

## Phase 1: The Bootloader (Birth)

**Goal:** Wake up the CPU and hand over control to your code.

### Step 1.1: The "Hello World" of OS Dev *(3 Days)*

**Concept:** The BIOS loads the first 512 bytes of the disk into memory (address `0x7C00`) and runs it.

**Action:**
- Write a simple Assembly file (`boot.asm`).
- Use `int 0x10` (BIOS interrupt) to print a character `'A'` to the screen.
- Compile using:
  ```bash
  nasm -f bin boot.asm -o boot.bin
  ```
- Run using:
  ```bash
  qemu-system-x86_64 -drive format=raw,file=boot.bin
  ```

> **Struggle:** The screen stays black.
> **Solution:** Check your infinite loop (`jmp $`) and magic number (`0xAA55` at the end of the 512 bytes).

---

### Step 1.2: Switching to 32-bit Protected Mode *(1 Week)*

**Concept:** The CPU starts in 16-bit "Real Mode" (legacy). We need to access more memory.

**Action:**
- Disable interrupts (`cli`).
- Load the GDT (Global Descriptor Table) — a map defining memory segments.
- Set the PE (Protection Enable) bit in the `CR0` register.
- Far jump to 32-bit code.

**Goal:** Print `"Hello from 32-bit mode"` using VGA memory (`0xB8000`) instead of BIOS interrupts.

---

### Step 1.3: Switching to 64-bit Long Mode *(1 Week)*

**Concept:** AI needs massive RAM. 32-bit only gives 4GB. We need 64-bit.

**Action:**
- Set up Paging (identity map the first 4MB).
- Enable PAE (Physical Address Extension).
- Set the Long Mode bit in `EFER MSR`.
- Enable Paging (set `CR3`).
- Far jump to 64-bit code.

> **Shortcut:** For now, use a Multiboot2 compliant bootloader (like GRUB) to handle Steps 1.2 and 1.3 for you. This lets you focus on the Kernel immediately.

---

## Phase 2: Kernel Foundation (The Heart)

**Goal:** Create a structured environment for C code.

### Step 2.1: The Kernel Entry Point *(3 Days)*

**Concept:** You need a stack pointer to call C functions.

**Action:**
- Write `boot.asm` to set up a stack (`mov esp, stack_top`).
- Call `kernel_main` from Assembly.
- Write `kernel.c`:
  ```c
  void kernel_main() {
      char* video_memory = (char*)0xB8000;
      *video_memory = 'X'; // Print X
  }
  ```
- Write a **Linker Script** (`linker.ld`) to tell the compiler where to place the kernel in memory.

---

### Step 2.2: Framebuffer Console *(1 Week)*

**Concept:** Writing to `0xB8000` byte-by-byte is tedious. You need a driver.

**Action:**
- Create `print.c`: Implement `print_string`, `print_int`, `clear_screen`.
- Handle scrolling (when text reaches the bottom of the screen).
- Handle cursor position tracking.

---

### Step 2.3: Global Descriptor Table (GDT) & Interrupts (IDT) *(2 Weeks)*

**Concept:** The CPU needs to know what to do when errors happen (like dividing by zero).

**Action:**
- Load a GDT (Code Segment, Data Segment).
- Remap the PIC (Programmable Interrupt Controller) to avoid conflicts with CPU exceptions.
- Load an IDT (Interrupt Descriptor Table).

> **Test:** Force a divide-by-zero error in your kernel. Your OS should catch it and print `"Error: Division by Zero"` instead of crashing/rebooting.

---

## Phase 3: Memory Management (The Sandbox)

**Goal:** Allocate memory dynamically. This is the hardest phase.

### Step 3.1: Physical Memory Manager *(1 Week)*

**Concept:** You need a map of which RAM addresses are free.

**Action:**
- Read the BIOS memory map (provided by Multiboot2).
- Create a "Bitmap Allocator": An array of bits where `1 = used`, `0 = free`.
- Implement `kalloc_physical_page()` and `kfree_physical_page()`.

---

### Step 3.2: Virtual Memory & Paging *(2 Weeks)*

**Concept:** Give every process its own "virtual" view of memory, isolating it from others.

**Action:**
- Map Virtual Addresses to Physical Addresses (`PML4 -> PDPT -> PD -> PT`).
- Implement `map_page(virtual_addr, physical_addr)`.

> **AIOS Twist:** Implement **Huge Pages (2MB)**. This reduces TLB (Translation Lookaside Buffer) misses, which is critical for large matrix operations in AI.

---

### Step 3.3: Kernel Heap (Malloc) *(1 Week)*

**Concept:** `kmalloc` allows you to create dynamic data structures (linked lists, trees).

**Action:**
- Implement a simple Heap Algorithm (e.g., First-Fit or Best-Fit).
- Define a block header (size, used flag, next pointer).

> **Test:** Allocate 1000 integers, free them, and check for memory leaks.

---

## Phase 4: Hardware Interaction (The Senses)

**Goal:** Interact with the outside world (Keyboard/Timer).

### Step 4.1: Keyboard Driver *(1 Week)*

**Concept:** The keyboard sends "Scan Codes", not ASCII letters.

**Action:**
- Handle IRQ1 (Interrupt Request 1).
- Read data from Port `0x60` (`in al, 0x60`).
- Create a Scancode → ASCII translation table.
- Implement a keyboard buffer (circular buffer) to store keystrokes.

---

### Step 4.2: Timer (PIT/APIC) *(3 Days)*

**Concept:** The OS needs a heartbeat for scheduling.

**Action:**
- Configure the PIT (Programmable Interval Timer) to fire 1000 times a second (1000Hz).
- Create a `timer_tick` global variable that increments on every interrupt.
- Implement `sleep(seconds)` function.

---

## Phase 5: File System (The Library)

**Goal:** Load the AI Model from disk.

### Step 5.1: Disk Driver (AHCI/IDE) *(2 Weeks)*

**Concept:** You need to read sectors from the hard drive.

**Action:**
- Start with simple PIO Mode IDE (Ports `0x1F0`).
- Function: `read_sector(lba_address, buffer)`.

> **Note:** AHCI (SATA) is faster but extremely complex. Stick to IDE or VirtIO for QEMU testing first.

---

### Step 5.2: Simple File System (FAT32) *(2 Weeks)*

**Concept:** You need a structure to organize files.

**Action:**
- Write a driver to read the FAT32 Boot Sector.
- Traverse the File Allocation Table to find clusters.
- Implement `fopen`, `fread`.

**Goal:** Read a text file stored on a virtual disk image.

---

## Phase 6: Multitasking (The Pulse)

**Goal:** Run multiple things at once.

### Step 6.1: Process Control Block (PCB) *(1 Week)*

**Concept:** A structure to save the state of a running program (Registers, Stack Pointer).

**Action:**
- Define `struct PCB` (pid, state, registers, stack_ptr).
- Create a process list.

---

### Step 6.2: Context Switching *(1 Week)*

**Concept:** The mechanism to pause one process and start another.

**Action:**
- In the Timer Interrupt handler, push all registers to the stack.
- Save the current Stack Pointer to the current PCB.
- Switch to the next PCB.
- Pop registers and return from interrupt.

---

### Step 6.3: The AIOS Scheduler *(1 Week)*

**Concept:** Standard Round-Robin is okay, but we want AI priority.

**Action:**
- Implement a Priority Queue.
- Assign **high priority** to User Input (Keyboard).
- Assign **lower priority** to Background Tasks (AI Inference).

---

## Phase 7: The AI Layer (The Brain)

**Goal:** Run the LLM locally.

### Step 7.1: SIMD/Math Setup *(1 Week)*

**Concept:** Enable AVX/SSE instructions in your OS.

**Action:**
- Enable FPU/SSE during boot (set `CR0`/`CR4` registers).
- Modify Context Switching to save FPU registers (`FXSAVE`).
- Write a Matrix Multiplication function using Assembly AVX2 intrinsics.

---

### Step 7.2: Model Inference Engine *(3 Weeks)*

**Concept:** The core logic.

**Action:**
- **Tokenization:** Port a simple BPE tokenizer to C (no standard lib).
- **Loader:** Write code to load binary weights from your File System into contiguous memory (use your "Tensor Allocator" from Phase 3).
- **Architecture:** Implement the Transformer layers (Dense layers, Softmax) in C.
- **Run:** Load a tiny model (e.g., "TinyStories" or a small GPT-2 checkpoint).

---

### Step 7.3: The Chat Loop *(1 Week)*

**Action:**
1. User types text.
2. OS Tokenizes text.
3. OS runs forward pass (Inference).
4. OS prints predicted token to screen.
5. Loop.

---

## Phase 8: User Interface (The Interaction)

**Goal:** A visual chat interface.

### Step 8.1: Graphics Mode *(2 Weeks)*

**Action:**
- Request a Linear Frame Buffer (LFB) from the bootloader/UEFI.
- Write a `put_pixel(x, y, color)` function.
- Load a bitmap font and draw text characters pixel-by-pixel.

---

### Step 8.2: The Shell *(1 Week)*

**Action:**
- Create a split screen: Top half for AI output, bottom half for user input.
- Implement scrolling text rendering.

---

## ✅ Summary Checklist: "Now Onwards"

| Week | Goal |
|------|------|
| **Week 1** | Install WSL2/Ubuntu, install `nasm`, `qemu`, build `x86_64-elf-gcc` |
| **Week 2** | Write a bootloader that prints `"Hi"` in 16-bit mode |
| **Week 3** | Switch to 64-bit mode and call a C `kernel_main` |
| **Week 4** | Implement Printing and Interrupts (IDT) |
| **Week 5–6** | Implement Physical and Virtual Memory (Paging) |
| **Week 7** | Implement Heap (`kmalloc`) |
| **Week 8** | Keyboard and Timer Drivers |
| **Week 9–10** | Disk Driver and FAT32 File System |
| **Week 11–12** | Multitasking and Scheduler |
| **Week 13+** | Implement AVX Math and port the LLM Inference Engine |
