#ifndef APIC_H
#define APIC_H

#include <stdint.h>

/* APIC — Advanced Programmable Interrupt Controller
 *
 * Local APIC: handles per-core interrupts (timer, IPIs, error).
 * I/O APIC  : handles external device interrupts (replaces PIC).
 *
 * AIOS Specific: Multi-core support for parallel AI tasks (SMP).
 * Each CPU core runs its own Local APIC.
 */

/* Local APIC register offsets (memory-mapped at LAPIC_BASE) */
#define LAPIC_BASE          0xFEE00000ULL
#define LAPIC_ID            0x020
#define LAPIC_VERSION       0x030
#define LAPIC_TPR           0x080   /* Task Priority Register */
#define LAPIC_EOI           0x0B0   /* End-Of-Interrupt */
#define LAPIC_SVR           0x0F0   /* Spurious Vector Register */
#define LAPIC_ICR_LOW       0x300   /* Interrupt Command Register lo */
#define LAPIC_ICR_HIGH      0x310   /* Interrupt Command Register hi */
#define LAPIC_TIMER_LVT     0x320
#define LAPIC_TIMER_INIT    0x380
#define LAPIC_TIMER_CURRENT 0x390
#define LAPIC_TIMER_DIVIDE  0x3E0

#define LAPIC_SVR_ENABLE    (1 << 8)
#define LAPIC_TIMER_PERIODIC (1 << 17)

/* I/O APIC */
#define IOAPIC_BASE         0xFEC00000ULL
#define IOAPIC_REGSEL       0x00
#define IOAPIC_IOWIN        0x10
#define IOAPIC_REDTBL_BASE  0x10

void     apic_init(void);            /* disable PIC, enable LAPIC + IOAPIC */
void     apic_eoi(void);             /* send End-Of-Interrupt to LAPIC */
uint32_t apic_get_id(void);          /* current core's LAPIC ID */
void     apic_send_ipi(uint8_t dest_apic_id, uint8_t vector); /* SMP IPI */
void     apic_timer_init(uint32_t ms_interval);  /* LAPIC timer */
void     ioapic_route(uint8_t irq, uint8_t vector, uint8_t dest_apic_id);

#endif /* APIC_H */
