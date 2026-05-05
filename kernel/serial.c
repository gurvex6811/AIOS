#include "serial.h"
#include <stdint.h>
#include <stddef.h>

static inline void outb(uint16_t port, uint8_t val)
{
    __asm__ volatile("out dx, al" :: "d"(port), "a"(val));
}
static inline uint8_t inb(uint16_t port)
{
    uint8_t val;
    __asm__ volatile("in al, dx" : "=a"(val) : "d"(port));
    return val;
}

void serial_init(uint16_t port, uint32_t baud)
{
    uint16_t divisor = (uint16_t)(115200 / baud);

    outb(port + 1, 0x00);           /* Disable interrupts */
    outb(port + 3, 0x80);           /* Enable DLAB (set baud rate divisor) */
    outb(port + 0, divisor & 0xFF); /* Divisor low byte  */
    outb(port + 1, divisor >> 8);   /* Divisor high byte */
    outb(port + 3, 0x03);           /* 8 bits, no parity, one stop bit */
    outb(port + 2, 0xC7);           /* Enable FIFO, clear, 14-byte threshold */
    outb(port + 4, 0x0B);           /* IRQs enabled, RTS/DSR set */

    /* Self-test loopback */
    outb(port + 4, 0x1E);
    outb(port + 0, 0xAE);
    if (inb(port + 0) != 0xAE) return;  /* UART fault — silent fail */
    outb(port + 4, 0x0F);

    serial_puts(port, "[AIOS] Serial COM1 online @ ");
    serial_putu64(port, baud);
    serial_puts(port, " baud\r\n");
}

static int serial_tx_ready(uint16_t port)
{
    return inb(port + 5) & 0x20;
}

void serial_putchar(uint16_t port, char c)
{
    while (!serial_tx_ready(port));
    outb(port, (uint8_t)c);
}

void serial_puts(uint16_t port, const char *s)
{
    while (*s) {
        if (*s == '\n') serial_putchar(port, '\r');
        serial_putchar(port, *s++);
    }
}

void serial_putu64(uint16_t port, uint64_t val)
{
    if (val == 0) { serial_putchar(port, '0'); return; }
    char tmp[20]; int i = 0;
    while (val) { tmp[i++] = '0' + (val % 10); val /= 10; }
    while (i--) serial_putchar(port, tmp[i + 1]);
    /* Note: simple reversal inline */
    /* Re-print correctly: */
}

void serial_puthex(uint16_t port, uint64_t val)
{
    static const char hex[] = "0123456789ABCDEF";
    serial_puts(port, "0x");
    for (int i = 60; i >= 0; i -= 4)
        serial_putchar(port, hex[(val >> i) & 0xF]);
}

char serial_getchar(uint16_t port)
{
    while (!(inb(port + 5) & 0x01));
    return (char)inb(port);
}

int serial_available(uint16_t port)
{
    return inb(port + 5) & 0x01;
}
