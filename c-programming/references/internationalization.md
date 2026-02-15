# Internationalization in C

C provides comprehensive support for internationalization (i18n) and localization through locale management, multibyte character encodings, and wide character handling. These features enable programs to adapt to different languages, cultures, and character sets.

## Locale Support with `<locale.h>`

### The Locale System

A locale defines cultural conventions for formatting, character classification, and text processing. The C library uses the current locale to determine behavior of various functions.

```c
#include <locale.h>
#include <stdio.h>

int main(void) {
    // Get current locale (initially "C" or "POSIX")
    char *current = setlocale(LC_ALL, NULL);
    printf("Current locale: %s\n", current);

    // Set to user's environment locale
    if (setlocale(LC_ALL, "") == NULL) {
        fprintf(stderr, "Failed to set locale from environment\n");
        return 1;
    }

    // Set specific locale
    setlocale(LC_ALL, "en_US.UTF-8");

    return 0;
}
```

### Locale Categories

The `setlocale()` function accepts category constants that control different aspects of localization:

- **`LC_COLLATE`** - String collation (strcoll, strxfrm)
- **`LC_CTYPE`** - Character classification and conversion (isalpha, toupper, multibyte functions)
- **`LC_MONETARY`** - Monetary formatting (localeconv)
- **`LC_NUMERIC`** - Numeric formatting (printf, scanf decimal point)
- **`LC_TIME`** - Time and date formatting (strftime)
- **`LC_ALL`** - All categories together

```c
// Set categories independently
setlocale(LC_NUMERIC, "de_DE.UTF-8");   // Use comma as decimal separator
setlocale(LC_TIME, "fr_FR.UTF-8");      // French date/time formatting
setlocale(LC_MONETARY, "en_GB.UTF-8");  // British currency formatting
```

### Numeric and Monetary Formatting with `localeconv()`

The `localeconv()` function returns a pointer to a `struct lconv` containing locale-specific formatting rules:

```c
#include <locale.h>
#include <stdio.h>

void display_locale_info(void) {
    struct lconv *lc = localeconv();

    // Numeric formatting
    printf("Decimal point: '%s'\n", lc->decimal_point);
    printf("Thousands separator: '%s'\n", lc->thousands_sep);
    printf("Grouping: %d\n", lc->grouping[0]);

    // Monetary formatting
    printf("Currency symbol: '%s'\n", lc->currency_symbol);
    printf("International currency: '%s'\n", lc->int_curr_symbol);
    printf("Monetary decimal point: '%s'\n", lc->mon_decimal_point);
    printf("Positive sign: '%s'\n", lc->positive_sign);
    printf("Negative sign: '%s'\n", lc->negative_sign);
    printf("Fractional digits: %d\n", lc->frac_digits);
    printf("Int'l fractional digits: %d\n", lc->int_frac_digits);
}

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");
    printf("=== US English ===\n");
    display_locale_info();

    setlocale(LC_ALL, "de_DE.UTF-8");
    printf("\n=== German ===\n");
    display_locale_info();

    return 0;
}
```

### Locale-Aware String Comparison

```c
#include <locale.h>
#include <string.h>
#include <stdio.h>

int main(void) {
    const char *words[] = {"apple", "äpfel", "banana", "zebra"};

    setlocale(LC_COLLATE, "de_DE.UTF-8");

    // strcoll uses locale-specific collation
    if (strcoll(words[0], words[1]) < 0) {
        printf("'%s' comes before '%s'\n", words[0], words[1]);
    }

    // strcmp uses byte values (locale-independent)
    if (strcmp(words[0], words[1]) < 0) {
        printf("Byte comparison: '%s' < '%s'\n", words[0], words[1]);
    }

    return 0;
}
```

### Locale Effects on Standard Functions

The locale affects many standard library functions:

```c
#include <locale.h>
#include <stdio.h>
#include <time.h>

int main(void) {
    double value = 1234.56;
    time_t now = time(NULL);
    struct tm *tm = localtime(&now);
    char buffer[100];

    // Default "C" locale
    printf("=== C Locale ===\n");
    printf("Number: %.2f\n", value);  // 1234.56
    strftime(buffer, sizeof(buffer), "%A, %B %d, %Y", tm);
    printf("Date: %s\n", buffer);  // Monday, February 15, 2026

    // German locale
    setlocale(LC_ALL, "de_DE.UTF-8");
    printf("\n=== German Locale ===\n");
    printf("Number: %.2f\n", value);  // 1234,56 (comma separator)
    strftime(buffer, sizeof(buffer), "%A, %B %d, %Y", tm);
    printf("Date: %s\n", buffer);  // Montag, Februar 15, 2026

    return 0;
}
```

## Multibyte Characters

Multibyte encodings represent extended character sets using variable-length byte sequences. UTF-8, Shift-JIS, and GB18030 are common multibyte encodings.

### Multibyte Character Properties

```c
#include <stdlib.h>
#include <limits.h>
#include <stdio.h>

int main(void) {
    // MB_CUR_MAX: max bytes per character in current locale
    printf("Max bytes per character: %d\n", MB_CUR_MAX);

    // MB_LEN_MAX: max bytes possible in any locale
    printf("Absolute max bytes: %d\n", MB_LEN_MAX);

    return 0;
}
```

### Examining Multibyte Sequences with `mblen()`

```c
#include <stdlib.h>
#include <locale.h>
#include <stdio.h>

void analyze_string(const char *str) {
    const char *p = str;
    int len;

    while (*p) {
        len = mblen(p, MB_CUR_MAX);

        if (len < 0) {
            printf("Invalid multibyte sequence\n");
            break;
        } else if (len == 0) {
            printf("Null character\n");
            break;
        } else {
            printf("Character (");
            for (int i = 0; i < len; i++) {
                printf("%02X ", (unsigned char)p[i]);
            }
            printf(") - %d byte%s\n", len, len > 1 ? "s" : "");
            p += len;
        }
    }
}

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    const char *text = "Hello, 世界";  // UTF-8 encoded
    analyze_string(text);

    return 0;
}
```

### Converting Between Multibyte and Wide Characters

```c
#include <stdlib.h>
#include <locale.h>
#include <stdio.h>

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    // Single character conversion
    const char *mb = "世";
    wchar_t wc;
    int bytes = mbtowc(&wc, mb, MB_CUR_MAX);
    printf("Converted %d bytes to wide char U+%04X\n", bytes, wc);

    // Convert back
    char mb_result[MB_LEN_MAX];
    int result = wctomb(mb_result, wc);
    printf("Wide char converted back to %d bytes\n", result);

    // String conversion
    const char *mb_string = "Hello, 世界";
    wchar_t wc_string[100];
    size_t count = mbstowcs(wc_string, mb_string, 100);
    printf("Converted %zu characters\n", count);

    // Convert back to multibyte
    char mb_back[200];
    size_t bytes_written = wcstombs(mb_back, wc_string, 200);
    printf("Converted back to %zu bytes: %s\n", bytes_written, mb_back);

    return 0;
}
```

### Reset Conversion State

```c
// Reset internal shift state for stateful encodings
mblen(NULL, 0);
mbtowc(NULL, NULL, 0);
wctomb(NULL, 0);
```

## Wide Characters

Wide characters (`wchar_t`) provide a fixed-width representation for extended character sets.

### Wide Character Basics

```c
#include <wchar.h>
#include <stdio.h>

int main(void) {
    // Wide character literals
    wchar_t wc = L'A';
    wchar_t wide_emoji = L'😊';  // May not work on all platforms

    // Wide string literals
    wchar_t *greeting = L"Hello, 世界";

    // Wide character range
    printf("wchar_t range: %d to %d\n", WCHAR_MIN, WCHAR_MAX);
    printf("Size of wchar_t: %zu bytes\n", sizeof(wchar_t));

    return 0;
}
```

## Wide String Operations with `<wchar.h>`

### Wide String Manipulation

```c
#include <wchar.h>
#include <stdio.h>

int main(void) {
    wchar_t dest[100];
    wchar_t *result;

    // String length
    const wchar_t *str = L"Hello, 世界";
    size_t len = wcslen(str);
    wprintf(L"Length: %zu\n", len);  // 9 characters, not bytes

    // Copy
    wcscpy(dest, L"Hello");
    wcsncpy(dest, L"Hi", 2);

    // Concatenate
    wcscat(dest, L", World");
    wcsncat(dest, L"!", 1);

    // Compare
    int cmp = wcscmp(L"apple", L"banana");
    cmp = wcsncmp(L"test", L"testing", 4);

    // Search
    result = wcschr(L"Hello", L'e');
    result = wcsrchr(L"Hello", L'l');
    result = wcsstr(L"Hello World", L"World");

    // Tokenize
    wchar_t text[] = L"one,two,three";
    wchar_t *token = wcstok(text, L",", &result);
    while (token) {
        wprintf(L"Token: %ls\n", token);
        token = wcstok(NULL, L",", &result);
    }

    return 0;
}
```

### Wide Character I/O

```c
#include <wchar.h>
#include <locale.h>
#include <stdio.h>

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    FILE *fp = fopen("wide_output.txt", "w");
    if (!fp) return 1;

    // Wide formatted output
    fwprintf(fp, L"Number: %d, String: %ls\n", 42, L"世界");
    wprintf(L"Console: %ls\n", L"Hello, 世界");

    // Single wide character I/O
    fputwc(L'A', fp);
    fputwc(L'\n', fp);

    // Wide string I/O
    fputws(L"Another line\n", fp);
    fclose(fp);

    // Reading
    fp = fopen("wide_output.txt", "r");
    wchar_t buffer[100];

    wint_t wc = fgetwc(fp);
    if (wc != WEOF) {
        wprintf(L"Read: %lc\n", wc);
    }

    if (fgetws(buffer, 100, fp)) {
        wprintf(L"Line: %ls", buffer);
    }

    // Formatted input
    int num;
    wchar_t str[50];
    rewind(fp);
    fwscanf(fp, L"Number: %d, String: %ls", &num, str);

    fclose(fp);
    return 0;
}
```

### Restartable Wide/Multibyte Conversion

For thread-safety and proper handling of stateful encodings, use the restartable conversion functions with `mbstate_t`:

```c
#include <wchar.h>
#include <locale.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    const char *mb = "Hello, 世界";
    wchar_t wc_buf[100];
    mbstate_t state;

    // Initialize state
    memset(&state, 0, sizeof(state));

    // Convert string with state tracking
    const char *src = mb;
    size_t result = mbsrtowcs(wc_buf, &src, 100, &state);
    wprintf(L"Converted %zu characters: %ls\n", result, wc_buf);

    // Convert single character
    memset(&state, 0, sizeof(state));
    src = mb;
    wchar_t wc;
    size_t bytes = mbrtowc(&wc, src, MB_CUR_MAX, &state);
    printf("First character used %zu bytes\n", bytes);

    // Convert wide to multibyte
    char mb_out[100];
    memset(&state, 0, sizeof(state));
    const wchar_t *wsrc = wc_buf;
    result = wcsrtombs(mb_out, &wsrc, 100, &state);
    printf("Converted back to %zu bytes: %s\n", result, mb_out);

    return 0;
}
```

## Wide Character Classification with `<wctype.h>`

### Classification Functions

```c
#include <wctype.h>
#include <wchar.h>
#include <locale.h>

void classify_wide(wchar_t wc) {
    wprintf(L"Character: %lc\n", wc);
    wprintf(L"  Alpha: %d\n", iswalpha(wc));
    wprintf(L"  Digit: %d\n", iswdigit(wc));
    wprintf(L"  Alnum: %d\n", iswalnum(wc));
    wprintf(L"  Space: %d\n", iswspace(wc));
    wprintf(L"  Upper: %d\n", iswupper(wc));
    wprintf(L"  Lower: %d\n", iswlower(wc));
    wprintf(L"  Punct: %d\n", iswpunct(wc));
    wprintf(L"  Cntrl: %d\n", iswcntrl(wc));
    wprintf(L"  Graph: %d\n", iswgraph(wc));
    wprintf(L"  Print: %d\n", iswprint(wc));
    wprintf(L"  Xdigit: %d\n", iswxdigit(wc));
}

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    classify_wide(L'A');
    classify_wide(L'5');
    classify_wide(L' ');
    classify_wide(L'世');

    return 0;
}
```

### Case Conversion

```c
#include <wctype.h>
#include <wchar.h>
#include <locale.h>

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    wchar_t str[] = L"Hello, 世界!";

    for (size_t i = 0; str[i]; i++) {
        if (iswlower(str[i])) {
            str[i] = towupper(str[i]);
        } else if (iswupper(str[i])) {
            str[i] = towlower(str[i]);
        }
    }

    wprintf(L"Result: %ls\n", str);
    return 0;
}
```

### Extensible Classification and Transformation

```c
#include <wctype.h>
#include <wchar.h>
#include <locale.h>

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    // Get character class descriptor
    wctype_t alpha_class = wctype("alpha");
    wctype_t punct_class = wctype("punct");

    wchar_t wc = L'A';
    if (iswctype(wc, alpha_class)) {
        wprintf(L"%lc is alphabetic\n", wc);
    }

    // Get transformation descriptor
    wctrans_t upper_trans = wctrans("toupper");
    wctrans_t lower_trans = wctrans("tolower");

    wchar_t result = towctrans(L'a', upper_trans);
    wprintf(L"towctrans('a', toupper) = %lc\n", result);

    return 0;
}
```

## Unicode Support in C11/C23

### UTF-16 and UTF-32 Types

C11 introduced fixed-size Unicode character types:

```c
#include <uchar.h>
#include <stdio.h>

int main(void) {
    // char16_t for UTF-16 (like JavaScript/Java char)
    char16_t u16_char = u'A';
    char16_t u16_emoji = u'😊';  // May need surrogate pair
    char16_t *u16_str = u"Hello, 世界";

    // char32_t for UTF-32 (one code point per character)
    char32_t u32_char = U'A';
    char32_t u32_emoji = U'😊';
    char32_t *u32_str = U"Hello, 世界";

    printf("Size of char16_t: %zu\n", sizeof(char16_t));
    printf("Size of char32_t: %zu\n", sizeof(char32_t));

    return 0;
}
```

### UTF-8 String Literals

```c
#include <stdio.h>

int main(void) {
    // C11: u8"" creates char[] with UTF-8 encoding
    const char *utf8 = u8"Hello, 世界";

    // C23: u8"" creates char8_t[]
    // const char8_t *utf8_c23 = u8"Hello, 世界";

    printf("UTF-8 string: %s\n", utf8);

    return 0;
}
```

### Converting Between Unicode Formats

```c
#include <uchar.h>
#include <locale.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    // UTF-32 to multibyte
    char32_t u32 = U'世';
    char mb[MB_LEN_MAX];
    mbstate_t state;
    memset(&state, 0, sizeof(state));

    size_t bytes = c32rtomb(mb, u32, &state);
    printf("UTF-32 to MB: %zu bytes\n", bytes);

    // Multibyte to UTF-32
    memset(&state, 0, sizeof(state));
    char32_t result32;
    bytes = mbrtoc32(&result32, mb, bytes, &state);
    printf("MB to UTF-32: U+%04X\n", result32);

    // UTF-16 conversion
    char16_t u16 = u'A';
    char mb16[MB_LEN_MAX];
    memset(&state, 0, sizeof(state));
    bytes = c16rtomb(mb16, u16, &state);
    printf("UTF-16 to MB: %zu bytes\n", bytes);

    // Multibyte to UTF-16
    memset(&state, 0, sizeof(state));
    char16_t result16;
    bytes = mbrtoc16(&result16, mb16, bytes, &state);
    printf("MB to UTF-16: U+%04X\n", result16);

    return 0;
}
```

## Practical Patterns

### Setting Locale in a Program

```c
#include <locale.h>
#include <stdio.h>
#include <stdlib.h>

int initialize_locale(void) {
    // Try to set from environment (LANG, LC_ALL, etc.)
    if (setlocale(LC_ALL, "") == NULL) {
        fprintf(stderr, "Warning: Could not set locale from environment\n");

        // Fallback to UTF-8 locale
        if (setlocale(LC_ALL, "en_US.UTF-8") == NULL) {
            fprintf(stderr, "Error: UTF-8 locale not available\n");
            return 0;
        }
    }

    printf("Locale set to: %s\n", setlocale(LC_ALL, NULL));
    return 1;
}

int main(void) {
    if (!initialize_locale()) {
        return EXIT_FAILURE;
    }

    // Rest of program...
    return EXIT_SUCCESS;
}
```

### Locale-Aware String Sorting

```c
#include <locale.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int compare_strings(const void *a, const void *b) {
    return strcoll(*(const char **)a, *(const char **)b);
}

int compare_wide_strings(const void *a, const void *b) {
    return wcscoll(*(const wchar_t **)a, *(const wchar_t **)b);
}

int main(void) {
    setlocale(LC_COLLATE, "de_DE.UTF-8");

    const char *words[] = {"Zebra", "Äpfel", "Banane", "Öl"};
    size_t count = sizeof(words) / sizeof(words[0]);

    qsort(words, count, sizeof(char *), compare_strings);

    printf("Sorted (German locale):\n");
    for (size_t i = 0; i < count; i++) {
        printf("  %s\n", words[i]);
    }

    return 0;
}
```

### Formatting Currency with Locale

```c
#include <locale.h>
#include <stdio.h>

void format_currency(double amount) {
    struct lconv *lc = localeconv();

    char sign = (amount < 0) ? *lc->negative_sign : *lc->positive_sign;
    double abs_amount = (amount < 0) ? -amount : amount;

    // Simple formatting (real implementation would handle positioning)
    printf("%c%s%.2f\n",
           sign,
           lc->currency_symbol,
           abs_amount);
}

int main(void) {
    double price = 1234.56;

    setlocale(LC_ALL, "en_US.UTF-8");
    printf("US: ");
    format_currency(price);

    setlocale(LC_ALL, "de_DE.UTF-8");
    printf("DE: ");
    format_currency(price);

    setlocale(LC_ALL, "en_GB.UTF-8");
    printf("GB: ");
    format_currency(price);

    return 0;
}
```

### Portable Locale Handling

```c
#include <locale.h>
#include <string.h>
#include <stdio.h>

// Save and restore locale
char *save_locale(int category) {
    char *current = setlocale(category, NULL);
    if (current) {
        return strdup(current);  // Caller must free
    }
    return NULL;
}

void restore_locale(int category, char *saved) {
    if (saved) {
        setlocale(category, saved);
        free(saved);
    }
}

void process_with_c_locale(void) {
    // Save current locale
    char *saved = save_locale(LC_NUMERIC);

    // Temporarily use C locale for parsing
    setlocale(LC_NUMERIC, "C");

    double value;
    sscanf("3.14159", "%lf", &value);  // Always uses '.'
    printf("Parsed: %f\n", value);

    // Restore original locale
    restore_locale(LC_NUMERIC, saved);
}

int main(void) {
    setlocale(LC_ALL, "de_DE.UTF-8");  // Uses comma
    process_with_c_locale();           // Temporarily uses dot

    // Back to German locale here
    printf("Number: %.2f\n", 1234.56);  // Outputs 1234,56

    return 0;
}
```

## Common Pitfalls

### Forgetting to Call `setlocale()`

```c
// WRONG: Locale functions won't work as expected
int main(void) {
    wprintf(L"Hello, 世界\n");  // May not display correctly
    return 0;
}

// CORRECT: Initialize locale first
int main(void) {
    setlocale(LC_ALL, "");
    wprintf(L"Hello, 世界\n");  // Will display correctly
    return 0;
}
```

### Assuming One Byte Equals One Character

```c
// WRONG: Incorrect for multibyte encodings
void count_chars_wrong(const char *str) {
    size_t count = strlen(str);  // Counts bytes, not characters
    printf("Characters: %zu\n", count);
}

// CORRECT: Use mbstowcs or count multibyte sequences
void count_chars_correct(const char *str) {
    wchar_t wc_buf[1000];
    size_t count = mbstowcs(wc_buf, str, 1000);
    printf("Characters: %zu\n", count);
}

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");
    const char *text = "Hello, 世界";

    count_chars_wrong(text);    // Prints 13 (bytes)
    count_chars_correct(text);  // Prints 9 (characters)

    return 0;
}
```

### Mixing Narrow and Wide I/O

```c
// WRONG: Cannot mix narrow and wide I/O on same stream
FILE *fp = fopen("file.txt", "w");
fprintf(fp, "Narrow\n");
fwprintf(fp, L"Wide\n");  // Undefined behavior!
fclose(fp);

// CORRECT: Choose one orientation per stream
FILE *fp1 = fopen("narrow.txt", "w");
fprintf(fp1, "Narrow only\n");
fclose(fp1);

FILE *fp2 = fopen("wide.txt", "w");
fwprintf(fp2, L"Wide only\n");
fclose(fp2);
```

### Platform-Specific `wchar_t` Size

```c
#include <wchar.h>
#include <stdio.h>

int main(void) {
    printf("wchar_t size: %zu bytes\n", sizeof(wchar_t));

    // Windows: typically 2 bytes (UTF-16)
    // Unix/Linux: typically 4 bytes (UTF-32)

    // Emoji may not fit in 2-byte wchar_t
    wchar_t emoji = L'😊';  // May be truncated on Windows

    // Use char32_t for guaranteed UTF-32
    char32_t emoji32 = U'😊';  // Always works

    return 0;
}
```

### Not Handling Conversion Errors

```c
#include <wchar.h>
#include <locale.h>
#include <stdio.h>
#include <errno.h>

int main(void) {
    setlocale(LC_ALL, "en_US.UTF-8");

    const char *invalid = "\xFF\xFE";  // Invalid UTF-8
    wchar_t wc_buf[100];

    errno = 0;
    size_t result = mbstowcs(wc_buf, invalid, 100);

    if (result == (size_t)-1) {
        perror("Conversion error");
        return 1;
    }

    wprintf(L"Converted: %ls\n", wc_buf);
    return 0;
}
```

### Locale Not Thread-Safe (Before C11)

```c
// WRONG: setlocale() affects entire process
void *thread_func(void *arg) {
    setlocale(LC_ALL, "de_DE.UTF-8");  // Affects all threads!
    // ... locale-dependent work
    return NULL;
}

// BETTER: Use per-thread locale (C11)
#ifdef __STDC_LIB_EXT1__
#include <threads.h>
thread_local locale_t thread_locale;

void *thread_func_safe(void *arg) {
    thread_locale = newlocale(LC_ALL_MASK, "de_DE.UTF-8", NULL);
    uselocale(thread_locale);
    // ... locale-dependent work
    freelocale(thread_locale);
    return NULL;
}
#endif
```

## Summary

C's internationalization features provide comprehensive support for:
- **Locale management** via `setlocale()` and category-specific control
- **Multibyte encodings** for variable-length character representations
- **Wide characters** for fixed-width processing
- **Unicode support** through char16_t, char32_t, and UTF-8 literals
- **Locale-aware operations** for formatting, collation, and classification

Key principles:
1. Always call `setlocale(LC_ALL, "")` early in main()
2. Use wide characters for internal processing, multibyte for I/O
3. Never mix narrow and wide I/O on the same stream
4. Check conversion function return values for errors
5. Be aware of platform differences in wchar_t size
6. Use restartable conversion functions for thread safety
7. Use strcoll/wcscoll for locale-aware string comparison

Mastering these features enables writing truly international software that adapts to different languages, scripts, and cultural conventions.
