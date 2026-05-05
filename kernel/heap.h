#ifndef HEAP_H
#define HEAP_H

#include <stddef.h>
#include <stdint.h>

/* Kernel Heap — free-list allocator (kmalloc / kfree)
 *
 * Block header is stored immediately before each allocation:
 *   [size | free | magic | next]
 * Aligned to 16 bytes throughout.
 */

#define HEAP_MAGIC  0xA110C8ED   /* "allocated" */

void  heap_init(uint64_t heap_start, size_t heap_size);
void *kmalloc(size_t size);
void *kmalloc_aligned(size_t size, size_t alignment);
void  kfree(void *ptr);
void *krealloc(void *ptr, size_t new_size);
void *kmemset(void *dst, int val, size_t n);
void *kmemcpy(void *dst, const void *src, size_t n);
void  heap_dump_stats(void);

#endif /* HEAP_H */
