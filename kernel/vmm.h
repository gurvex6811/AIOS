#ifndef VMM_H
#define VMM_H

#include <stdint.h>
#include <stddef.h>

/* Virtual Memory Manager — 4-level paging (PML4)
 *
 * Virtual address breakdown (48-bit canonical):
 *   [47:39] PML4 index  (9 bits)
 *   [38:30] PDPT  index (9 bits)
 *   [29:21] PD    index (9 bits)
 *   [20:12] PT    index (9 bits)
 *   [11:0]  Page  offset (12 bits)
 */

#define PAGE_PRESENT    (1ULL << 0)
#define PAGE_WRITE      (1ULL << 1)
#define PAGE_USER       (1ULL << 2)
#define PAGE_HUGE       (1ULL << 7)   /* 2 MB pages in PD */
#define PAGE_NX         (1ULL << 63)  /* No-execute */

#define VIRT_TO_PHYS_OFFSET  0xFFFFFFFF80000000ULL  /* kernel higher-half */

typedef uint64_t page_entry_t;

void     vmm_init(void);
void     vmm_map_page(uint64_t virt, uint64_t phys, uint64_t flags);
void     vmm_unmap_page(uint64_t virt);
uint64_t vmm_virt_to_phys(uint64_t virt);
void     vmm_map_range(uint64_t virt_start, uint64_t phys_start, size_t page_count, uint64_t flags);
void     vmm_switch_directory(uint64_t pml4_phys);
uint64_t vmm_get_current_pml4(void);

#endif /* VMM_H */
