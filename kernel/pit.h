#ifndef PIT_H
#define PIT_H

#include <stdint.h>

/* PIT — Programmable Interval Timer (Intel 8253/8254)
 * Channel 0, Mode 3 (square wave), IRQ 0 → INT 0x20.
 * Default frequency: 100 Hz (10 ms tick).
 */

#define PIT_CHANNEL0    0x40
#define PIT_COMMAND     0x43
#define PIT_BASE_FREQ   1193182UL   /* Hz */
#define PIT_HZ          100         /* Target tick rate */

void     pit_init(uint32_t hz);
void     pit_handler(void);         /* called from ISR 0 */
uint64_t pit_get_ticks(void);
uint64_t pit_get_ms(void);
void     pit_sleep_ms(uint64_t ms);

#endif /* PIT_H */
