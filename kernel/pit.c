#include "pit.h"
#include "vga.h"
#include <stdint.h>

static volatile uint64_t ticks = 0;
static uint32_t tick_hz = PIT_HZ;

static inline void outb(uint16_t port, uint8_t val)
{
    __asm__ volatile("out dx, al" :: "d"(port), "a"(val));
}

void pit_init(uint32_t hz)
{
    tick_hz = hz;
    uint32_t divisor = PIT_BASE_FREQ / hz;

    /* Channel 0, lo/hi byte, Mode 3 (square wave), binary */
    outb(PIT_COMMAND, 0x36);
    outb(PIT_CHANNEL0, (uint8_t)(divisor & 0xFF));
    outb(PIT_CHANNEL0, (uint8_t)((divisor >> 8) & 0xFF));

    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("  [ OK ] PIT timer @ ");
    vga_putu64(hz);
    vga_puts(" Hz\n");
    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
}

void pit_handler(void)
{
    ticks++;
    /* Send EOI */
    __asm__ volatile("out 0x20, al" :: "a"((uint8_t)0x20));
}

uint64_t pit_get_ticks(void) { return ticks; }

uint64_t pit_get_ms(void)    { return ticks * 1000 / tick_hz; }

void pit_sleep_ms(uint64_t ms)
{
    uint64_t target = pit_get_ms() + ms;
    while (pit_get_ms() < target) __asm__ volatile("hlt");
}
