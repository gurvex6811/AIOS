#include "keyboard.h"
#include "vga.h"
#include <stdint.h>
#include <stddef.h>

/* ─── Scan code set 1 → ASCII (unshifted) ──────────── */
static const uint8_t sc_to_ascii[128] = {
    0,   27,  '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=',  '\b',
    '\t','q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0,   'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',
    0,   '\\','z','x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0,
    '*', 0,   ' ', 0,
    /* F1-F10, NumLock, ScrollLock, KP7-9... simplified to 0 */
    [0x3B ... 0x7F] = 0
};

static const uint8_t sc_to_ascii_shift[128] = {
    0,   27,  '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+',  '\b',
    '\t','Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '\n',
    0,   'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', '~',
    0,   '|', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 0,
    '*', 0,   ' ', 0,
    [0x3B ... 0x7F] = 0
};

/* ─── Ring buffer ─────────────────────────────────── */
static key_event_t buf[KBD_BUF_SIZE];
static volatile int buf_head = 0;
static volatile int buf_tail = 0;
static uint8_t      shift_held = 0;
static uint8_t      ctrl_held  = 0;

static inline uint8_t inb(uint16_t port)
{
    uint8_t val;
    __asm__ volatile("in al, dx" : "=a"(val) : "d"(port));
    return val;
}

static inline void outb(uint16_t port, uint8_t val)
{
    __asm__ volatile("out dx, al" :: "d"(port), "a"(val));
}

void keyboard_init(void)
{
    /* Flush output buffer */
    while (inb(KBD_STATUS_PORT) & 0x01) inb(KBD_DATA_PORT);

    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("  [ OK ] PS/2 Keyboard driver ready\n");
    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
}

void keyboard_handler(void)
{
    uint8_t sc = inb(KBD_DATA_PORT);
    int key_down = !(sc & 0x80);
    uint8_t code = sc & 0x7F;

    /* Track modifier keys */
    if (code == 0x2A || code == 0x36) { shift_held = key_down; return; }
    if (code == 0x1D)                 { ctrl_held  = key_down; return; }
    if (!key_down) return;            /* ignore key-up for printable keys */

    uint8_t ascii = shift_held ? sc_to_ascii_shift[code] : sc_to_ascii[code];

    int next = (buf_head + 1) % KBD_BUF_SIZE;
    if (next != buf_tail) {
        buf[buf_head].scancode = code;
        buf[buf_head].ascii    = ascii;
        buf[buf_head].flags    = (key_down ? 1 : 0) | (shift_held ? 2 : 0) | (ctrl_held ? 4 : 0);
        buf_head = next;
    }

    /* Send EOI to PIC */
    outb(0x20, 0x20);
}

int keyboard_get_event(key_event_t *out)
{
    if (buf_head == buf_tail) return 0;
    *out = buf[buf_tail];
    buf_tail = (buf_tail + 1) % KBD_BUF_SIZE;
    return 1;
}

uint8_t keyboard_getchar(void)
{
    key_event_t e;
    while (!keyboard_get_event(&e)) {
        __asm__ volatile("hlt");
    }
    return e.ascii;
}

size_t keyboard_readline(char *kbuf, size_t max_len)
{
    size_t i = 0;
    while (i < max_len - 1) {
        uint8_t c = keyboard_getchar();
        if (c == '\n') { vga_putchar('\n'); break; }
        if (c == '\b') {
            if (i > 0) { i--; vga_putchar('\b'); }
            continue;
        }
        if (c) { kbuf[i++] = c; vga_putchar(c); }
    }
    kbuf[i] = '\0';
    return i;
}

int keyboard_available(void) { return buf_head != buf_tail; }
