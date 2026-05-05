#include "pci.h"
#include "vga.h"
#include <stdint.h>

static pci_device_t devices[PCI_MAX_DEVICES];
static int          device_count = 0;

static inline void outl(uint16_t port, uint32_t val)
{
    __asm__ volatile("out dx, eax" :: "d"(port), "a"(val));
}
static inline uint32_t inl(uint16_t port)
{
    uint32_t val;
    __asm__ volatile("in eax, dx" : "=a"(val) : "d"(port));
    return val;
}

uint32_t pci_read(uint8_t bus, uint8_t dev, uint8_t fn, uint8_t offset)
{
    uint32_t addr = (1u << 31)
                  | ((uint32_t)bus    << 16)
                  | ((uint32_t)dev    << 11)
                  | ((uint32_t)fn     <<  8)
                  | (offset & 0xFC);
    outl(PCI_CONFIG_ADDR, addr);
    return inl(PCI_CONFIG_DATA);
}

void pci_write(uint8_t bus, uint8_t dev, uint8_t fn, uint8_t offset, uint32_t val)
{
    uint32_t addr = (1u << 31)
                  | ((uint32_t)bus    << 16)
                  | ((uint32_t)dev    << 11)
                  | ((uint32_t)fn     <<  8)
                  | (offset & 0xFC);
    outl(PCI_CONFIG_ADDR, addr);
    outl(PCI_CONFIG_DATA, val);
}

void pci_enumerate(void)
{
    device_count = 0;
    for (uint16_t bus = 0; bus < PCI_MAX_BUS; bus++) {
        for (uint8_t dev = 0; dev < PCI_MAX_DEVICE; dev++) {
            for (uint8_t fn = 0; fn < PCI_MAX_FUNCTION; fn++) {
                uint32_t id = pci_read(bus, dev, fn, 0x00);
                if ((id & 0xFFFF) == 0xFFFF) continue;  /* no device */

                if (device_count >= PCI_MAX_DEVICES) goto done;

                pci_device_t *d = &devices[device_count++];
                d->bus       = bus;
                d->device    = dev;
                d->function  = fn;
                d->vendor_id = id & 0xFFFF;
                d->device_id = (id >> 16) & 0xFFFF;

                uint32_t cls = pci_read(bus, dev, fn, 0x08);
                d->class_code = (cls >> 24) & 0xFF;
                d->subclass   = (cls >> 16) & 0xFF;
                d->prog_if    = (cls >>  8) & 0xFF;

                uint32_t hdr = pci_read(bus, dev, fn, 0x0C);
                d->header_type = (hdr >> 16) & 0xFF;

                for (int b = 0; b < 6; b++)
                    d->bar[b] = pci_read(bus, dev, fn, 0x10 + b * 4);

                uint32_t irq = pci_read(bus, dev, fn, 0x3C);
                d->irq_line = irq & 0xFF;

                /* Single-function device: skip remaining functions */
                if (fn == 0 && !(d->header_type & 0x80)) break;
            }
        }
    }
done:
    vga_set_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_puts("  [ OK ] PCI enumerated — ");
    vga_putu64(device_count);
    vga_puts(" device(s) found\n");
    vga_set_color(VGA_COLOR_LIGHT_GREY, VGA_COLOR_BLACK);
}

void pci_init(void) { pci_enumerate(); }

pci_device_t *pci_find_device(uint8_t class_code, uint8_t subclass)
{
    for (int i = 0; i < device_count; i++) {
        if (devices[i].class_code == class_code &&
            devices[i].subclass   == subclass) {
            return &devices[i];
        }
    }
    return NULL;
}

int pci_get_device_count(void) { return device_count; }

void pci_dump(void)
{
    for (int i = 0; i < device_count; i++) {
        pci_device_t *d = &devices[i];
        vga_puts("  PCI ");
        vga_putu64(d->bus);
        vga_putchar(':');
        vga_putu64(d->device);
        vga_putchar('.');
        vga_putu64(d->function);
        vga_puts("  VendorID=");
        vga_putu64(d->vendor_id);
        vga_puts("  Class=");
        vga_putu64(d->class_code);
        vga_putchar('.');
        vga_putu64(d->subclass);
        vga_putchar('\n');
    }
}
