# Java 11 Date/Time and Localization
## java.time API, LocalDate/ZonedDateTime/Instant, Duration/Period, DateTimeFormatter, Locale, ResourceBundle

---

## `java.time` Overview

The `java.time` API (Java 8+, JSR-310) replaces the deprecated `java.util.Date` and `java.util.Calendar`. It is immutable, thread-safe, and clear about timezone handling.

```
┌─────────────────────────────────────────────────────┐
│                   java.time                          │
│                                                     │
│  LocalDate       — date only (no time, no zone)    │
│  LocalTime       — time only (no date, no zone)    │
│  LocalDateTime   — date + time (no zone)           │
│  ZonedDateTime   — date + time + zone              │
│  OffsetDateTime  — date + time + UTC offset        │
│  OffsetTime      — time + UTC offset               │
│  Instant         — machine timestamp (UTC epoch)   │
│                                                     │
│  Duration        — amount of time (seconds/nanos)  │
│  Period          — amount of date (years/months/days)│
│                                                     │
│  ZoneId          — timezone (e.g. "America/New_York")│
│  ZoneOffset      — UTC offset (e.g. +05:30)        │
└─────────────────────────────────────────────────────┘
```

---

## `LocalDate`

```java
LocalDate today = LocalDate.now();
LocalDate date  = LocalDate.of(2024, Month.MARCH, 15);
LocalDate date  = LocalDate.of(2024, 3, 15);
LocalDate date  = LocalDate.parse("2024-03-15");   // ISO-8601

date.getYear()          // 2024
date.getMonth()         // Month.MARCH
date.getMonthValue()    // 3
date.getDayOfMonth()    // 15
date.getDayOfWeek()     // DayOfWeek.FRIDAY
date.getDayOfYear()     // 75
date.lengthOfMonth()    // 31
date.isLeapYear()       // false

// Arithmetic (immutable — returns new instance)
date.plusDays(7)
date.plusWeeks(2)
date.plusMonths(1)
date.plusYears(1)
date.minusDays(3)
date.withDayOfMonth(1)   // first of month
date.withMonth(6)

// Comparison
date.isBefore(other)
date.isAfter(other)
date.isEqual(other)
date.compareTo(other)    // -1, 0, 1
```

---

## `LocalTime`

```java
LocalTime now  = LocalTime.now();
LocalTime time = LocalTime.of(14, 30, 0);         // 14:30:00
LocalTime time = LocalTime.of(14, 30, 0, 500_000_000); // with nanoseconds
LocalTime time = LocalTime.parse("14:30:00");

time.getHour()           // 14
time.getMinute()         // 30
time.getSecond()         // 0
time.getNano()

time.plusHours(2)
time.minusMinutes(15)
time.withHour(9)

LocalTime.MIDNIGHT    // 00:00
LocalTime.NOON        // 12:00
```

---

## `LocalDateTime`

```java
LocalDateTime ldt = LocalDateTime.now();
LocalDateTime ldt = LocalDateTime.of(2024, 3, 15, 14, 30);
LocalDateTime ldt = LocalDateTime.of(date, time);
LocalDateTime ldt = LocalDateTime.parse("2024-03-15T14:30:00");

ldt.toLocalDate()
ldt.toLocalTime()
ldt.plusDays(1).minusHours(2)
```

---

## `ZonedDateTime`

Always use `ZonedDateTime` (or `OffsetDateTime`) when storing/transmitting times that must survive daylight saving transitions.

```java
ZonedDateTime zdt = ZonedDateTime.now();
ZonedDateTime zdt = ZonedDateTime.now(ZoneId.of("America/New_York"));
ZonedDateTime zdt = ZonedDateTime.of(2024, 3, 15, 14, 30, 0, 0,
    ZoneId.of("Europe/London"));
ZonedDateTime zdt = ZonedDateTime.parse("2024-03-15T14:30:00-05:00[America/New_York]");

zdt.getZone()            // ZoneId
zdt.getOffset()          // ZoneOffset (e.g. -05:00)
zdt.toLocalDateTime()
zdt.toInstant()

// Convert timezone
ZonedDateTime tokyo = zdt.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));
```

### Common Zone IDs

```java
ZoneId.of("UTC")
ZoneId.of("America/New_York")
ZoneId.of("America/Los_Angeles")
ZoneId.of("Europe/London")
ZoneId.of("Europe/Paris")
ZoneId.of("Asia/Tokyo")
ZoneId.systemDefault()           // JVM default timezone
ZoneId.getAvailableZoneIds()     // all ~600 zone IDs
```

---

## `Instant`

Machine-readable UTC timestamp — nanosecond precision since Unix epoch (1970-01-01T00:00:00Z).

```java
Instant now = Instant.now();
Instant ts  = Instant.ofEpochSecond(1700000000L);
Instant ts  = Instant.ofEpochMilli(System.currentTimeMillis());
Instant ts  = Instant.parse("2024-03-15T14:30:00Z");

ts.getEpochSecond()
ts.getNano()
ts.toEpochMilli()

ts.plusSeconds(60)
ts.isBefore(other)
ts.isAfter(other)

// Convert to ZonedDateTime
ZonedDateTime zdt = ts.atZone(ZoneId.of("America/New_York"));

// Convert from ZonedDateTime
Instant i = zdt.toInstant();
```

---

## `Duration` vs. `Period`

| | `Duration` | `Period` |
|-|-----------|---------|
| Measures | Time (hours, minutes, seconds, nanos) | Dates (years, months, days) |
| Works with | `Instant`, `LocalTime`, `LocalDateTime` | `LocalDate` |
| Daylight saving aware | No (fixed seconds) | Yes (calendar-aware) |

```java
// Duration
Duration d = Duration.ofHours(2).plusMinutes(30);
Duration d = Duration.between(start, end);
d.toHours()
d.toMinutes()
d.toSeconds()
d.toMillis()
d.isNegative()

// Period
Period p = Period.of(1, 6, 15);   // 1 year, 6 months, 15 days
Period p = Period.between(LocalDate.of(2020, 1, 1), LocalDate.now());
p.getYears()
p.getMonths()
p.getDays()
p.toTotalMonths()

// Apply
LocalDate future = LocalDate.now().plus(Period.ofMonths(6));
LocalDateTime later = LocalDateTime.now().plus(Duration.ofHours(3));
```

---

## `DateTimeFormatter`

```java
import java.time.format.DateTimeFormatter;

// Predefined
DateTimeFormatter.ISO_LOCAL_DATE       // "2024-03-15"
DateTimeFormatter.ISO_LOCAL_DATE_TIME  // "2024-03-15T14:30:00"
DateTimeFormatter.ISO_ZONED_DATE_TIME  // "2024-03-15T14:30:00-05:00[America/New_York]"
DateTimeFormatter.ISO_INSTANT          // "2024-03-15T19:30:00Z"

// Custom pattern
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("MMM d, yyyy", Locale.US);

// Format
String s = LocalDate.now().format(fmt);
String s = ZonedDateTime.now().format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);

// Parse
LocalDate   d = LocalDate.parse("15/03/2024", fmt);
LocalDateTime dt = LocalDateTime.parse("2024-03-15T14:30:00");
ZonedDateTime zdt = ZonedDateTime.parse("2024-03-15T14:30:00-05:00[America/New_York]");
```

### Pattern Letters

| Letter | Meaning | Example |
|--------|---------|---------|
| `yyyy` | Year (4-digit) | 2024 |
| `MM` | Month (2-digit) | 03 |
| `MMM` | Month abbreviation | Mar |
| `MMMM` | Month full | March |
| `dd` | Day of month | 15 |
| `HH` | Hour 24h | 14 |
| `hh` | Hour 12h | 02 |
| `mm` | Minutes | 30 |
| `ss` | Seconds | 00 |
| `SSS` | Milliseconds | 123 |
| `a` | AM/PM | PM |
| `z` | Zone name | EST |
| `Z` | Zone offset | -0500 |
| `VV` | Zone ID | America/New_York |

---

## `Locale`

Represents a language/country combination for localization.

```java
Locale us = Locale.US;                          // predefined constant
Locale fr = Locale.FRANCE;
Locale jp = Locale.JAPAN;
Locale custom = new Locale("pt", "BR");         // Portuguese, Brazil
Locale tag = Locale.forLanguageTag("zh-Hans-CN"); // IETF BCP 47 tag

Locale.getDefault()       // JVM default locale
Locale.getAvailableLocales()

locale.getLanguage()      // "en"
locale.getCountry()       // "US"
locale.getDisplayName()   // "English (United States)"
locale.toLanguageTag()    // "en-US"
```

---

## `NumberFormat`

```java
NumberFormat nf = NumberFormat.getInstance(Locale.US);
nf.format(1234567.89)    // "1,234,567.89"

NumberFormat currency = NumberFormat.getCurrencyInstance(Locale.US);
currency.format(1234.5)  // "$1,234.50"

NumberFormat pct = NumberFormat.getPercentInstance(Locale.US);
pct.format(0.75)         // "75%"

// Parse
Number n = NumberFormat.getInstance(Locale.US).parse("1,234.56");
double d = n.doubleValue();
```

---

## `ResourceBundle`

Externalize locale-specific strings outside code.

### Property Files

```
messages.properties      (default)
messages_fr.properties   (French)
messages_fr_FR.properties (French, France)
```

```properties
# messages.properties
greeting=Hello
farewell=Goodbye

# messages_fr.properties
greeting=Bonjour
farewell=Au revoir
```

### Loading

```java
ResourceBundle bundle = ResourceBundle.getBundle("messages");            // default locale
ResourceBundle bundle = ResourceBundle.getBundle("messages", Locale.FRANCE);

String greeting = bundle.getString("greeting");

// Check existence
bundle.containsKey("greeting");
bundle.keySet();   // Set<String>
```

### Java Class Bundle

```java
public class Messages_fr extends ListResourceBundle {
    @Override
    protected Object[][] getContents() {
        return new Object[][] {
            {"greeting", "Bonjour"},
            {"farewell", "Au revoir"}
        };
    }
}
```

Bundle lookup order (most specific first):
`language_country_variant` → `language_country` → `language` → default file

---

## `MessageFormat`

Format messages with placeholders:

```java
String pattern = "Hello, {0}! You have {1} messages.";
String result = MessageFormat.format(pattern, "Alice", 5);
// "Hello, Alice! You have 5 messages."

// With locale-aware formatting
MessageFormat mf = new MessageFormat("On {0,date,long}, you earned {1,number,currency}", Locale.US);
String s = mf.format(new Object[]{new Date(), 1234.56});
// "On March 15, 2024, you earned $1,234.56"
```

---

## Legacy Date/Time Interop

Convert between `java.time` and legacy `java.util.Date` / `java.util.Calendar`:

```java
// Date → Instant
Instant instant = legacyDate.toInstant();

// Instant → Date
Date date = Date.from(instant);

// Date → LocalDateTime
LocalDateTime ldt = legacyDate.toInstant()
    .atZone(ZoneId.systemDefault())
    .toLocalDateTime();

// LocalDateTime → Date
Date date = Date.from(
    localDateTime.atZone(ZoneId.systemDefault()).toInstant());

// Calendar → ZonedDateTime
ZonedDateTime zdt = calendar.toInstant()
    .atZone(calendar.getTimeZone().toZoneId());
```

---

## Temporal Adjusters

```java
import java.time.temporal.TemporalAdjusters;

LocalDate firstOfMonth = date.with(TemporalAdjusters.firstDayOfMonth());
LocalDate lastOfMonth  = date.with(TemporalAdjusters.lastDayOfMonth());
LocalDate nextMonday   = date.with(TemporalAdjusters.next(DayOfWeek.MONDAY));
LocalDate firstMonday  = date.with(TemporalAdjusters.firstInMonth(DayOfWeek.MONDAY));

// Custom adjuster
TemporalAdjuster nextWorkday = d -> {
    LocalDate ld = (LocalDate) d;
    return switch (ld.getDayOfWeek()) {
        case FRIDAY -> ld.plusDays(3);
        case SATURDAY -> ld.plusDays(2);
        default -> ld.plusDays(1);
    };
};
```
