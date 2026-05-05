#ifndef AHCI_H
#define AHCI_H

#include <stdint.h>
#include <stddef.h>

/* AHCI — Advanced Host Controller Interface (SATA)
 * Provides read/write access to SATA disks via HBA MMIO registers.
 * PCI Class 0x01, Subclass 0x06.
 *
 * AIOS Specific: required for loading model weight files from disk.
 */

/* HBA Memory Registers */
#define AHCI_HBA_CAP     0x00  /* Host Capabilities */
#define AHCI_HBA_GHC     0x04  /* Global HBA Control */
#define AHCI_HBA_IS      0x08  /* Interrupt Status */
#define AHCI_HBA_PI      0x0C  /* Ports Implemented */
#define AHCI_HBA_VS      0x10  /* Version */

#define AHCI_GHC_AHCI_ENABLE  (1 << 31)
#define AHCI_GHC_RESET        (1 <<  0)

/* Port register offsets (rel