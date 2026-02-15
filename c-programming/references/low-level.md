# Low-Level Programming

Low-level programming in C involves direct manipulation of bits, hardware interaction, and understanding the underlying memory and data representation. This chapter covers bitwise operations, memory layout, alignment, endianness, and techniques for working close to the hardware.

## Bitwise Operators

C provides six bitwise operators that work on integer operands at the bit level:

### Basic Bitwise Operators

**Bitwise AND (`&`)**: Sets each bit to 1 if both bits are 1
```c
unsigned char a = 0xA3;  // 10100011
unsigned char b = 0x5F;  // 01011111
unsigned char c = a & b; // 00000011 = 0x03
```

**Bitwise OR (`|`)**: Sets each bit to 1 if at least one bit is 1
```c
unsigned char a = 0xA3;  // 10100011
unsigned char b = 0x5F;  // 01011111
unsigned char c = a | b; // 11111111 = 0xFF
```

**Bitwise XOR (`^`)**: Sets each bit to 1 if exactly one bit is 1
```c
unsigned char a = 0xA3;  // 10100011
unsigned char b = 0x5F;  // 01011111
unsigned char c = a ^ b; // 11111100 = 0xFC
```

**Bitwise NOT (`~`)**: Inverts all bits (unary operator)
```c
unsigned char a = 0xA3;  // 10100011
unsigned char b = ~a;    // 01011100 = 0x5C
```

### Shift Operators

**Left Shift (`<<`)**: Shifts bits left, filling with zeros
```c
unsigned char a = 0x13;   // 00010011
unsigned char b = a << 2; // 01001100 = 0x4C
// Equivalent to multiplying by 2^2 = 4
```

**Right Shift (`>>`)**: Shifts bits right
```c
unsigned char a = 0x4C;   // 01001100
unsigned char b = a >> 2; // 00010011 = 0x13

// For signed types, behavior is implementation-defined
// Most implementations do arithmetic shift (sign extension)
signed char c = -4;       // 11111100 (assuming 8-bit)
signed char d = c >> 1;   // 11111110 (sign bit copied)
```

### Operator Precedence Warnings

Bitwise operators have **lower precedence** than comparison operators, which is counterintuitive:

```c
// WRONG: this is parsed as (flags & (MASK == MASK))
if (flags & MASK == MASK)

// CORRECT: use parentheses
if ((flags & MASK) == MASK)

// WRONG: this is parsed as (x & (1 != 0))
if (x & 1 != 0)

// CORRECT
if ((x & 1) != 0)
```

Precedence from highest to lowest: `~` > `<<` `>>` > `&` > `^` > `|`

## Common Bit Manipulation Idioms

### Set a Bit
```c
unsigned int flags = 0;
unsigned int bit_position = 3;

// Set bit 3 to 1
flags |= (1U << bit_position);
```

### Clear a Bit
```c
unsigned int flags = 0xFF;
unsigned int bit_position = 3;

// Set bit 3 to 0
flags &= ~(1U << bit_position);
```

### Toggle a Bit
```c
unsigned int flags = 0x0A;
unsigned int bit_position = 3;

// Flip bit 3
flags ^= (1U << bit_position);
```

### Test a Bit
```c
unsigned int flags = 0x0A;
unsigned int bit_position = 3;

// Check if bit 3 is set
if (flags & (1U << bit_position)) {
    // Bit is set
}

// Alternative: get boolean result
int is_set = !!(flags & (1U << bit_position));
```

### Extract a Bit Field
```c
// Extract bits [7:4] from a byte
unsigned char value = 0xA3;  // 10100011
unsigned int shift = 4;
unsigned int width = 4;

unsigned int field = (value >> shift) & ((1U << width) - 1);
// field = 0x0A (1010)
```

### Insert a Bit Field
```c
// Insert 4-bit field at position 4
unsigned char value = 0x03;    // 00000011
unsigned int field = 0x0A;     // 1010
unsigned int shift = 4;
unsigned int width = 4;

// Create mask and clear target bits
unsigned char mask = ((1U << width) - 1) << shift;
value = (value & ~mask) | ((field << shift) & mask);
// value = 0xA3 (10100011)
```

### Create a Bitmask
```c
// Create mask with N lowest bits set
unsigned int width = 5;
unsigned int mask = (1U << width) - 1;  // 0x1F = 00011111

// Create mask for bits [high:low]
unsigned int low = 3, high = 6;
unsigned int range_mask = (((1U << (high - low + 1)) - 1) << low);
// 0x78 = 01111000
```

### Check if Power of Two
```c
// A power of 2 has exactly one bit set
unsigned int n = 16;

// Returns true for powers of 2, false otherwise
int is_power_of_2 = (n != 0) && ((n & (n - 1)) == 0);
```

## Bit-Fields in Structs

Bit-fields allow you to specify the width of struct members in bits:

### Declaration
```c
struct file_flags {
    unsigned int read_only : 1;
    unsigned int hidden    : 1;
    unsigned int system    : 1;
    unsigned int archive   : 1;
    unsigned int reserved  : 4;  // 4 unused bits
};

struct ip_header {
    unsigned int version        : 4;
    unsigned int header_length  : 4;
    unsigned int service_type   : 8;
    unsigned int total_length   : 16;
};
```

### Portability Issues

**Bit Ordering**: The order in which bits are allocated within a storage unit is implementation-defined:

```c
struct bits {
    unsigned int a : 4;
    unsigned int b : 4;
};

// On some systems: [b3 b2 b1 b0 a3 a2 a1 a0]
// On others:       [a3 a2 a1 a0 b3 b2 b1 b0]
```

**Signedness**: Whether a bit-field of type `int` is signed or unsigned is implementation-defined. Always use `unsigned int` or `signed int` explicitly.

```c
// AVOID: signedness is implementation-defined
struct bad {
    int flag : 1;  // Could be signed or unsigned!
};

// GOOD: explicit signedness
struct good {
    unsigned int flag : 1;
};
```

**Alignment and Padding**: Compilers may add padding between or after bit-fields.

### When to Use Bit-Fields vs Manual Bit Manipulation

**Use bit-fields when:**
- Working with internal data structures
- Code clarity is more important than portability
- Not performing byte-level I/O

**Use manual bit manipulation when:**
- Parsing binary file formats
- Working with network protocols
- Need precise control over memory layout
- Portability across different compilers/architectures is critical

## volatile Qualifier

The `volatile` qualifier tells the compiler that a variable's value may change in ways not visible to the optimizer.

### What It Means

```c
volatile int hardware_register;

// The compiler will NOT optimize these reads/writes
int a = hardware_register;
int b = hardware_register;  // Actually reads twice (not optimized away)

hardware_register = 1;
hardware_register = 2;  // Both writes happen (not combined)
```

Without `volatile`, the compiler might:
- Cache values in registers
- Eliminate "redundant" reads
- Reorder or combine memory accesses

### Use Cases

**Hardware Registers**: Memory-mapped I/O locations
```c
#define UART_STATUS  (*(volatile unsigned char *)0x40001000)
#define UART_DATA    (*(volatile unsigned char *)0x40001004)

// Wait for transmitter ready
while (!(UART_STATUS & 0x80))
    ;  // volatile ensures status is re-read each iteration

UART_DATA = 'A';  // Write to data register
```

**Signal Handlers**: Variables modified by signal handlers
```c
volatile sig_atomic_t signal_received = 0;

void signal_handler(int sig) {
    signal_received = 1;
}

int main(void) {
    signal(SIGINT, signal_handler);

    while (!signal_received) {
        // volatile ensures signal_received is checked each iteration
    }
}
```

**Shared Memory**: Variables shared between threads or processes (though atomic operations are usually better)

### Volatile Pointers

```c
// Pointer to volatile data
volatile int *p1;  // *p1 is volatile

// Volatile pointer to non-volatile data
int * volatile p2;  // p2 is volatile

// Volatile pointer to volatile data
volatile int * volatile p3;  // Both are volatile
```

## Memory Layout

A typical C program's memory is organized into several segments:

### Typical Program Memory Layout

```
High addresses
+------------------+
|      Stack       |  Local variables, function parameters
|        |         |  Grows downward
|        v         |
+------------------+
|                  |
|   Unused space   |
|                  |
+------------------+
|        ^         |
|        |         |  Grows upward
|      Heap        |  Dynamically allocated memory (malloc)
+------------------+
|   BSS Segment    |  Uninitialized global/static variables
+------------------+
|   Data Segment   |  Initialized global/static variables
+------------------+
|   Text Segment   |  Program code (read-only)
+------------------+
Low addresses
```

**Text Segment**: Contains executable instructions, typically read-only and sharable.

**Data Segment**: Contains initialized global and static variables.
```c
int global_init = 42;        // In data segment
static int static_init = 10; // In data segment
```

**BSS Segment**: Contains uninitialized (zero-initialized) global and static variables.
```c
int global_uninit;        // In BSS
static int static_uninit; // In BSS
```

**Heap**: Dynamically allocated memory grows upward.
```c
int *p = malloc(sizeof(int));  // Allocated on heap
```

**Stack**: Automatic variables, function call frames, grows downward.
```c
void func(int param) {  // param on stack
    int local = 42;     // local on stack
}
```

### Understanding Addresses

```c
#include <stdio.h>

int global = 42;
static int static_var = 100;
int bss_var;

int main(void) {
    int local = 1;
    int *heap = malloc(sizeof(int));

    printf("Text:    %p (main function)\n", (void *)main);
    printf("Data:    %p (global)\n", (void *)&global);
    printf("Data:    %p (static_var)\n", (void *)&static_var);
    printf("BSS:     %p (bss_var)\n", (void *)&bss_var);
    printf("Heap:    %p (malloc'd)\n", (void *)heap);
    printf("Stack:   %p (local)\n", (void *)&local);

    free(heap);
    return 0;
}
```

## Alignment

Alignment refers to the memory address at which data is stored. Many architectures require or prefer that data be aligned to specific boundaries.

### Natural Alignment

Most types have a natural alignment equal to their size:

```c
char c;      // 1-byte alignment (any address)
short s;     // 2-byte alignment (even addresses)
int i;       // 4-byte alignment (addresses divisible by 4)
long l;      // 4 or 8-byte alignment (platform-dependent)
double d;    // 8-byte alignment (addresses divisible by 8)
```

Structs are aligned to the alignment of their most-strictly-aligned member:

```c
struct example {
    char c;     // 1 byte
    // 3 bytes padding
    int i;      // 4 bytes (requires 4-byte alignment)
    short s;    // 2 bytes
    // 2 bytes padding (to make struct size multiple of 4)
};
// sizeof(struct example) == 12, not 7
```

### Alignment Requirements

**Unaligned Access**: On some architectures (x86), unaligned access is allowed but slower. On others (ARM without special modes), it causes a fault.

```c
char buffer[8];
int *p = (int *)(buffer + 1);  // Likely unaligned!
*p = 42;  // May crash or be slow
```

### C11 Alignment Operators

**`_Alignof`**: Query the alignment requirement of a type
```c
#include <stdalign.h>

size_t align = alignof(double);  // Typically 8
printf("double alignment: %zu\n", align);
```

**`_Alignas`**: Specify alignment for a variable
```c
#include <stdalign.h>

// Align to 16-byte boundary (useful for SIMD)
alignas(16) char buffer[64];

// Ensure struct is cache-line aligned
alignas(64) struct data {
    int values[16];
};
```

### GCC-Specific Alignment

```c
// Align variable to 64-byte boundary
char buffer[256] __attribute__((aligned(64)));

// Specify alignment for a type
typedef struct {
    int data[8];
} aligned_struct __attribute__((aligned(32)));
```

## Endianness

Endianness refers to the byte order used to store multi-byte values in memory.

### Big-Endian vs Little-Endian

For the 32-bit value `0x12345678`:

**Big-Endian**: Most significant byte first
```
Address:  0x1000  0x1001  0x1002  0x1003
Value:      12      34      56      78
```

**Little-Endian**: Least significant byte first
```
Address:  0x1000  0x1001  0x1002  0x1003
Value:      78      56      34      12
```

### Detecting Endianness

```c
int is_big_endian(void) {
    union {
        uint32_t i;
        char c[4];
    } test = { 0x01020304 };

    return test.c[0] == 1;  // True if big-endian
}

// Alternative: compile-time detection
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    // Big-endian system
#elif __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    // Little-endian system
#endif
```

### Byte Swapping

```c
#include <stdint.h>

uint16_t swap16(uint16_t x) {
    return (x >> 8) | (x << 8);
}

uint32_t swap32(uint32_t x) {
    return ((x >> 24) & 0x000000FF) |
           ((x >> 8)  & 0x0000FF00) |
           ((x << 8)  & 0x00FF0000) |
           ((x << 24) & 0xFF000000);
}

// Many compilers provide builtins
uint32_t value = __builtin_bswap32(0x12345678);
```

### Network Byte Order

Network protocols use big-endian (network byte order). POSIX provides conversion functions:

```c
#include <arpa/inet.h>

uint32_t host_value = 0x12345678;

// Host to network (long/short)
uint32_t net_value = htonl(host_value);
uint16_t net_port = htons(8080);

// Network to host
uint32_t back_to_host = ntohl(net_value);
uint16_t host_port = ntohs(net_port);
```

## Union Type Punning

Type punning is reinterpreting the bytes of one type as another type.

### Reading Different Member Than Written

```c
union float_bits {
    float f;
    uint32_t bits;
};

union float_bits fb;
fb.f = 3.14159f;

// Read the bit pattern of a float
printf("Float bits: 0x%08X\n", fb.bits);
```

### Strict Aliasing Implications

C's strict aliasing rule says you can only access an object through:
- Its declared type
- A compatible type
- A character type

Type punning through unions is **allowed in C** (but not C++):

```c
// LEGAL in C (undefined in C++)
union converter {
    float f;
    uint32_t u;
} conv;

conv.f = 3.14f;
uint32_t bits = conv.u;  // OK in C
```

### memcpy Alternative

The portable way that works in both C and C++:

```c
float f = 3.14f;
uint32_t bits;

memcpy(&bits, &f, sizeof(float));
// Compiler optimizes this to direct copy
```

## Working with Hardware

### Memory-Mapped I/O Patterns

Hardware registers appear at fixed memory addresses:

```c
// Define register addresses
#define GPIO_BASE    0x40020000

#define GPIOA_MODER  (*(volatile uint32_t *)(GPIO_BASE + 0x00))
#define GPIOA_ODR    (*(volatile uint32_t *)(GPIO_BASE + 0x14))
#define GPIOA_IDR    (*(volatile uint32_t *)(GPIO_BASE + 0x10))

// Set pin 5 as output
GPIOA_MODER = (GPIOA_MODER & ~(3U << 10)) | (1U << 10);

// Set pin 5 high
GPIOA_ODR |= (1U << 5);

// Read pin 3
int state = (GPIOA_IDR >> 3) & 1;
```

### Volatile Pointers to Hardware Registers

```c
struct uart_registers {
    volatile uint32_t data;
    volatile uint32_t status;
    volatile uint32_t control;
    volatile uint32_t baud_rate;
};

#define UART0 ((struct uart_registers *)0x40010000)

void uart_send_byte(uint8_t byte) {
    // Wait for transmit ready
    while (!(UART0->status & 0x80))
        ;
    UART0->data = byte;
}
```

### Bit-Banding Concept

Some ARM Cortex-M processors support bit-banding: a memory region where each bit can be addressed individually.

```c
// Bit-band alias formula (Cortex-M)
#define BITBAND_ADDR(addr, bit) \
    (0x42000000 + ((addr) - 0x40000000) * 32 + (bit) * 4)

#define GPIO_PIN_5_BIT \
    (*(volatile uint32_t *)BITBAND_ADDR(0x40020014, 5))

// Atomic bit set (single instruction)
GPIO_PIN_5_BIT = 1;
```

## Packed Structures

Packed structures eliminate padding between members.

### Using #pragma pack

```c
#pragma pack(push, 1)  // Save current packing, set to 1-byte
struct packet_header {
    uint8_t type;
    uint16_t length;
    uint32_t sequence;
};
#pragma pack(pop)  // Restore previous packing

// sizeof(struct packet_header) == 7 (no padding)
```

### GCC __attribute__((packed))

```c
struct packet_header {
    uint8_t type;
    uint16_t length;
    uint32_t sequence;
} __attribute__((packed));
```

### Network Protocol Structures

```c
#pragma pack(push, 1)
struct tcp_header {
    uint16_t source_port;
    uint16_t dest_port;
    uint32_t seq_number;
    uint32_t ack_number;
    uint8_t data_offset;
    uint8_t flags;
    uint16_t window;
    uint16_t checksum;
    uint16_t urgent_ptr;
} __attribute__((packed));
#pragma pack(pop)

// Read from network buffer
void parse_tcp(const uint8_t *buffer) {
    struct tcp_header *hdr = (struct tcp_header *)buffer;
    uint16_t port = ntohs(hdr->dest_port);
    // ...
}
```

### Binary File Formats

```c
#pragma pack(push, 1)
struct bmp_header {
    uint16_t signature;    // 'BM'
    uint32_t file_size;
    uint16_t reserved1;
    uint16_t reserved2;
    uint32_t data_offset;
};
#pragma pack(pop)

FILE *f = fopen("image.bmp", "rb");
struct bmp_header hdr;
fread(&hdr, sizeof(hdr), 1, f);

if (hdr.signature != 0x4D42) {  // 'BM' in little-endian
    fprintf(stderr, "Not a BMP file\n");
}
```

### Warnings About Packed Structures

**Unaligned Access**: Packed structures may cause unaligned accesses:

```c
struct packed {
    uint8_t a;
    uint32_t b;  // Only 1-byte aligned!
} __attribute__((packed));

struct packed p;
uint32_t *ptr = &p.b;  // May cause issues
*ptr = 42;  // Potential unaligned access
```

**Portability**: Use explicit byte-swapping for multi-byte fields in portable code.

## Integer Representation

### Two's Complement

C23 requires two's complement representation for signed integers. Practically all modern systems use it.

In two's complement for N-bit signed integers:
- Range: -2^(N-1) to 2^(N-1) - 1
- Negation: flip all bits and add 1
- Most significant bit is the sign bit

```c
int8_t x = -5;
// Binary: 11111011
// To negate: ~11111011 + 1 = 00000100 + 1 = 00000101 = 5

// Interesting property: -x == ~x + 1
assert(-x == (~x + 1));
```

### Sign Extension

When converting to a wider signed type, the sign bit is replicated:

```c
int8_t x = -5;     // 11111011
int16_t y = x;     // 1111111111111011 (sign extended)

// Explicit sign extension
int8_t narrow = -5;
int32_t wide = (int32_t)narrow;  // Automatic sign extension

// Manual sign extension from arbitrary width
uint32_t sign_extend(uint32_t value, unsigned int bits) {
    uint32_t m = 1U << (bits - 1);  // Sign bit mask
    return (value ^ m) - m;
}
```

### Truncation Behavior

When converting to a narrower type, high-order bits are discarded:

```c
int32_t x = 0x12345678;
int16_t y = (int16_t)x;  // 0x5678 (low 16 bits)
int8_t z = (int8_t)x;    // 0x78 (low 8 bits)

// Truncation preserves value modulo 2^N
assert(y == (x & 0xFFFF));
assert(z == (x & 0xFF));
```

### Overflow Behavior

Unsigned integer overflow is well-defined (wraps modulo 2^N):
```c
uint8_t x = 255;
x++;  // x == 0 (well-defined)
```

Signed integer overflow is **undefined behavior** in C:
```c
int x = INT_MAX;
x++;  // UNDEFINED BEHAVIOR!
```

To detect potential overflow:
```c
// Safe addition check
int safe_add(int a, int b, int *result) {
    if (b > 0 && a > INT_MAX - b) return 0;  // Overflow
    if (b < 0 && a < INT_MIN - b) return 0;  // Underflow
    *result = a + b;
    return 1;
}
```
