#ifndef PCI_H
#define PCI_H

#include <stdint.h>

/* PCI Bus Enumeration
 * Uses Configuration Space Access Mechanism #1 (I/O ports 0xCF8 / 0xCFC).
 */

#define PCI_CONFIG_ADDR  0xCF8
#define PCI_CONFIG_DATA  0xCFC

#define PCI_MAX_BUS      256
#define PCI_MAX_DEVICE   32
#define PCI_MAX_FUNCTION 8

typedef struct {
    uint8_t  bus;
    uint8_t  device;
    uint8_t  function;
    uint16_t vendor_id;
    uint16_t device_id;
    uint8_t  class_code;
    uint8_t  subclass;
    uint8_t  prog_if;
    uint8_t  header_type;
    uint32_t bar[6];        /* Base Address Registers */
    uint8_t  irq_line;
} pci_device_t;

#define PCI_MAX_DEVICES  64

void        pci_init(void);
void        pci_enumerate(void);
uint32_t    pci_read(uint8_t bus, uint8_t dev, uint8_t fn, uint8_t offset);
void        pci_write(uint8_t bus, uint8_t dev, uint8_t fn, uint8_t offset, uint32_t val);
pci_device_t *pci_find_device(uint8_t class_code, uint8_t subclass);
int         pci_get_device_count(void);
void        pci_dump(void);

#endif /* PCI_H */
