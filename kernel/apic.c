#include "apic.h"
#include "vga.h"
#include <stdint.h>

/* ─── MMIO helpers ────────────────────────────────── */
static inline uint32_t lapic_read(uint32_t offset)
{
    return *((volatile uint32_t *)(LAPIC_BASE + offset));
}
static inline void lapic_write(uint32_t offset, uint32_t val)
{
    *((volatile uint32_t *)(LAPIC_BASE + offset)) = val;
}

static inline void ioapic_write(uint8_t reg, uint32_t val)
{
    *((volatile uint32_t *)(IOAPIC_BASE + IOAPIC_REGSEL)) = reg;
    *((volatile uint32_t *)(IOAPIC_BASE + IOAPIC_IOWIN))  = val;
}
static inline uint32_t ioapic_read(uint8_t reg)
{
    *((volatile uint32_t *)(IOAPIC_BASE + IOAPIC_REGSEL)) = reg;
    return *((volatile uint32_t *)(IOAPIC_BASE + IOAPIC_IOWIN));
}

/* ─── Disable legacy 8259 PIC ─────────────────────── */
static void pic_disable(void)
{
    __asm__ volatile(
        "mov al, 0xFF\n"
        "out 0xA1, al\n"   /* mask all slave  PIC IRQs */
        "out 0x21, al\n"   /* mask all master PIC IRQs */
        ::: "eax"
    );
}

/* ─── apic_init ───────────────────────────────────── */
void apic_init(void)
{
    /* 1. Disable legacy PIC */
    pic_disable();

    /* 2. Enable Local APIC via IA32_APIC_BASE MSR */
    uint64_t msr;
    __asm__ volatile(
        "mov ecx, 0x1B\n"
        "rdmsr\n"
        "or  eax, 0x800\n"   /* set APIC global enable bit */
        "wrmsr\n"
        ::: "eax", "ecx", "edx"
    );
    (void)msr;

    /* 3. Set Spurious Vector Register → enable LAPIC, spurious vector = 0xFF */
    lapic_write(LAPIC_SVR, LAPIC_SVR_ENABLE | 0xFF);

    /* 4. Zero TPR (accept all interrupts) */
    lapic_write(LAPIC_TPR, 0);

    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("  [ OK ] LAPIC enabled (ID=");
    vga_putu64(apic_get_id());
    vga_puts(")\n");
    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
}

void apic_eoi(void)
{
    lapic_write(LAPIC_EOI, 0);
}

uint32_t apic_get_id(void)
{
    return (lapic_read(LAPIC_ID) >> 24) & 0xFF;
}

void apic_send_ipi(uint8_t dest_apic_id, uint8_t vector)
{
    lapic_write(LAPIC_ICR_HIGH, (uint32_t)dest_apic_id << 24);
    lapic_write(LAPIC_ICR_LOW,  (1 << 14) | vector);   /* assert, fixed delivery */
}

void apic_timer_init(uint32_t ms_interval)
{
    /* Calibrate: divide by 16, one-shot first to measure, then periodic */
    lapic_write(LAPIC_TIMER_DIVIDE, 0x03);   /* divide by 16 */
    lapic_write(LAPIC_TIMER_LVT,    LAPIC_TIMER_PERIODIC | 0x20); /* INT 0x20 */
    lapic_write(LAPIC_TIMER_INIT,   ms_interval * 100000);        /* approx */
}

void ioapic_route(uint8_t irq, uint8_t vector, uint8_t dest_apic_id)
{
    uint8_t  reg_lo = IOAPIC_REDTBL_BASE + irq * 2;
    uint8_t  reg_hi = reg_lo + 1;
    /* High 32-bits: destination APIC ID */
    ioapic_write(reg_hi, (uint32_t)dest_apic_id << 24);
    /* Low  32-bits: vector, fixed delivery, edge-triggered, unmasked */
    ioapic_write(reg_lo, vector);
}
