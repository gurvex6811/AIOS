#ifndef KEYBOARD_H
#define KEYBOARD_H

#include <stdint.h>
#include <stddef.h>

/* PS/2 Keyboard Driver
 * Scan code set 1 → ASCII mapping.
 * Ring buffer for key events, non-blocking reads.
 */

#define KBD_DATA_PORT   0x60
#define KBD_STATUS_PORT 0x64
#define KBD_BUF_SIZE    256

typedef struct {
    uint8_t scancode;
    uint8_t ascii;
    uint8_t flags;      /* bit 0 = key_down, bit 1 = shift, bit 2 = ctrl */
} key_event_t;

void  keyboard_init(void);
void  keyboard_handler(void);         /* called from ISR 1 */
int   keyboard_get_event(key_event_t *out);
uint8_t keyboard_getchar(void);       /* blocking read */
size_t keyboard_readline(char *buf, size_t max_len);
int   keyboard_available(void);

#endif /* KEYBOARD_H */
