/* ============================================================
 * AIOS — Kernel Main
 * Entry point called from boot/kernel_entry.asm
 * Phase 1: Foundation  +  Input Subsystem (keyboard + mouse)
 * ============================================================ */

#include "include/vga.h"
#include "include/gdt.h"
#include "include/idt.h"
#include "include/keyboard.h"
#include "include/mouse.h"
#include <stdint.h>

/* Multiboot2 magic value passed in EAX by GRUB */
#define MULTIBOOT2_MAGIC 0x36D76289

/* PIC I/O ports */
#define PIC1_DATA  0x21
#define PIC2_DATA  0xA1

static inline void outb(uint16_t port, uint8_t val) {
    __asm__ volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}
static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    __asm__ volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

/* ── IRQ dispatcher wrappers ─────────────────────────────── */
static void kbd_isr(interrupt_frame_t *frame) {
    (void)frame;
    keyboard_handle_irq();
}

static void mouse_isr(interrupt_frame_t *frame) {
    (void)frame;
    mouse_handle_irq();
}

/* ── Helpers ─────────────────────────────────────────────── */
static void print_banner(void) {
    vga_puts_color(
        "======================================================\n",
        VGA_COLOR_CYAN, VGA_COLOR_BLACK);
    vga_puts_color(
        "   AIOS \xC3\xB6 Autonomous Intelligent Operating System     \n",
        VGA_COLOR_WHITE, VGA_COLOR_BLACK);
    vga_puts_color(
        "   Phase 1: Foundation                               \n",
        VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts_color(
        "======================================================\n",
        VGA_COLOR_CYAN, VGA_COLOR_BLACK);
    vga_puts("\n");
}

static void print_ok(const char *label) {
    vga_puts_color("  [ ",  VGA_COLOR_LIGHT_GREY,  VGA_COLOR_BLACK);
    vga_puts_color("OK",    VGA_COLOR_LIGHT_GREEN,  VGA_COLOR_BLACK);
    vga_puts_color(" ] ",   VGA_COLOR_LIGHT_GREY,  VGA_COLOR_BLACK);
    vga_puts(label);
    vga_puts("\n");
}

/* ── Kernel entry ────────────────────────────────────────── */
void kernel_main(uint32_t mb2_magic, uint32_t mb2_info_ptr) {
    (void)mb2_info_ptr;

    /* 1. VGA text driver */
    vga_init();
    print_banner();

    /* 2. Multiboot2 check */
    if (mb2_magic == MULTIBOOT2_MAGIC) {
        print_ok("Multiboot2 handoff verified");
    } else {
        vga_puts_color(
            "  [WARN] Not booted via Multiboot2 \xC3\xB6 some features may differ\n",
            VGA_COLOR_BROWN, VGA_COLOR_BLACK);
    }

    /* 3. GDT */
    gdt_init();
    print_ok("GDT loaded (null / kernel-code / kernel-data / user-code / user-data)");

    /* 4. IDT + PIC remap */
    idt_init();
    print_ok("IDT loaded, PIC remapped (IRQ0-15 \xe2\x86\x92 INT 0x20-0x2F)");
    print_ok("STI \xe2\x80\x94 interrupts enabled");

    /* 5. Keyboard: register handler for INT 0x21 (IRQ1) */
    idt_register_handler(0x21, kbd_isr);
    keyboard_init();

    /* 6. Mouse: register handler for INT 0x2C (IRQ12) */
    idt_register_handler(0x2C, mouse_isr);
    mouse_init();

    /* 7. Unmask IRQ1 (keyboard) on PIC1, IRQ12 (mouse) on PIC2.
     *    idt_init() restores the masks it read at startup; we
     *    explicitly clear the bits we need here. */
    uint8_t mask1 = inb(PIC1_DATA);
    uint8_t mask2 = inb(PIC2_DATA);
    mask1 &= (uint8_t)~(1 << 1);   /* unmask IRQ1  (keyboard) */
    mask1 &= (uint8_t)~(1 << 2);   /* unmask IRQ2  (cascade to PIC2) */
    mask2 &= (uint8_t)~(1 << 4);   /* unmask IRQ12 (mouse) */
    outb(PIC1_DATA, mask1);
    outb(PIC2_DATA, mask2);
    print_ok("PIC masks: IRQ1 (kbd) + IRQ12 (mouse) unmasked");

    /* ── Phase 1 complete ─────────────────────────────────── */
    vga_puts("\n");
    vga_puts_color(
        "  AIOS Initialized\n",
        VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("\n");
    vga_puts_color(
        "  Input subsystem active. Type on keyboard or move mouse.\n",
        VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK);
    vga_puts("\n");

    /* ── Idle loop ────────────────────────────────────────── */
    for (;;) {
        __asm__ volatile ("hlt");
    }
}
