# Notifications

From Chapter 8 of *Java Management Extensions* by J. Steven Perry.

## Overview

The JMX notification model is a publish/subscribe system built into the MBean infrastructure. Any MBean can emit notifications; any object can subscribe.

Key classes:
- `Notification` — the event object
- `NotificationListener` — callback interface
- `NotificationFilter` — optional pre-filter before delivery
- `NotificationBroadcaster` / `NotificationEmitter` — implemented by MBeans that emit
- `NotificationBroadcasterSupport` — base class that handles listener bookkeeping

## The Notification Class

```java
public class Notification extends EventObject {
    private String type;       // dot-separated type string, e.g. "com.example.cache.eviction"
    private long sequenceNumber;
    private long timeStamp;
    private Object userData;   // application-specific payload
    private String message;    // human-readable description
}
```

### Constructing a Notification

```java
// Constructor: (type, source, sequenceNumber, timeStamp, message)
Notification notif = new Notification(
    "com.example.cache.eviction",   // type
    this,                            // source (the MBean)
    nextSequenceNumber(),            // sequence number
    System.currentTimeMillis(),      // timestamp
    "Evicted item: " + key           // message
);
notif.setUserData(evictedEntry);     // optional payload
```

## NotificationBroadcaster Interface

```java
public interface NotificationBroadcaster {
    void addNotificationListener(NotificationListener listener,
                                  NotificationFilter filter,
                                  Object handback)
        throws IllegalArgumentException;

    void removeNotificationListener(NotificationListener listener)
        throws ListenerNotFoundException;

    MBeanNotificationInfo[] getNotificationInfo();
}
```

`NotificationEmitter` extends `NotificationBroadcaster` with a three-arg `removeNotificationListener` that removes a specific listener+filter+handback triple (useful when the same listener is registered multiple times with different filters).

## Making an MBean a Broadcaster

Extend `NotificationBroadcasterSupport`:

```java
public class Cache extends NotificationBroadcasterSupport implements CacheMBean {
    private long sequenceNumber = 0;

    // Override to document notification types (shown in JMX consoles)
    @Override
    public MBeanNotificationInfo[] getNotificationInfo() {
        return new MBeanNotificationInfo[]{
            new MBeanNotificationInfo(
                new String[]{"com.example.cache.eviction",
                             "com.example.cache.overflow"},
                Notification.class.getName(),
                "Cache lifecycle notifications"
            )
        };
    }

    private void evict(String key) {
        // ... eviction logic ...
        Notification n = new Notification(
            "com.example.cache.eviction",
            this,
            ++sequenceNumber,
            System.currentTimeMillis(),
            "Evicted: " + key
        );
        sendNotification(n);  // dispatches to all registered listeners
    }
}
```

## Registering a Listener

### Direct listener on an MBean

```java
mbs.addNotificationListener(cacheName, myListener, myFilter, handbackObject);
mbs.removeNotificationListener(cacheName, myListener);
```

### Listener as a callback lambda

```java
mbs.addNotificationListener(cacheName,
    (notification, handback) -> {
        System.out.println("Received: " + notification.getType()
            + " seq=" + notification.getSequenceNumber());
    },
    null,   // no filter
    null    // no handback
);
```

### MBean listening to another MBean

An MBean itself can implement `NotificationListener`:

```java
public class AlertManager implements AlertManagerMBean, NotificationListener {
    @Override
    public void handleNotification(Notification notification, Object handback) {
        // handback is whatever was passed at registration time
        String tag = (String) handback;
        processAlert(tag, notification);
    }
}

// Register it as a listener on the Cache MBean
mbs.addNotificationListener(cacheName, alertManager, null, "cache-alert");
```

## NotificationFilter

Filters run synchronously before delivery, in the broadcaster's thread. Keep them fast.

### NotificationFilterSupport (built-in)

```java
NotificationFilterSupport filter = new NotificationFilterSupport();
filter.enableType("com.example.cache.eviction");   // whitelist
filter.disableType("com.example.cache.overflow");  // blacklist

mbs.addNotificationListener(cacheName, listener, filter, null);
```

`enableType` adds the type prefix to the enabled set; `disableType` removes it. A notification is delivered if its type starts with any enabled prefix.

### Custom Filter

```java
NotificationFilter highPriorityOnly = (notification) -> {
    if (notification.getUserData() instanceof Map) {
        Map<?,?> data = (Map<?,?>) notification.getUserData();
        return Integer.valueOf(5).equals(data.get("priority"));
    }
    return false;
};
```

## AttributeChangeNotification

A standard subclass for attribute value changes:

```java
AttributeChangeNotification acn = new AttributeChangeNotification(
    this,                            // source
    ++sequenceNumber,
    System.currentTimeMillis(),
    "MaxSize changed",               // message
    "MaxSize",                       // attribute name
    "int",                           // attribute type
    oldValue,                        // old value
    newValue                         // new value
);
sendNotification(acn);
```

Declare this in `getNotificationInfo()`:

```java
new MBeanNotificationInfo(
    new String[]{AttributeChangeNotification.ATTRIBUTE_CHANGE},
    AttributeChangeNotification.class.getName(),
    "Fired when attributes change"
)
```

## Sequence Number Management

Each broadcaster should maintain a monotonically increasing sequence number. Use `AtomicLong` for thread safety:

```java
private final AtomicLong sequenceNumber = new AtomicLong(0);

// In notification creation:
long seq = sequenceNumber.incrementAndGet();
```

Consumers use sequence numbers to detect missed notifications (gaps) or reordering in remote scenarios.

## Notification Delivery Guarantees

- **In-process**: delivery is synchronous by default in `NotificationBroadcasterSupport`; listeners are called in the broadcaster's thread
- **Remote**: the JSR 160 connector buffers notifications; clients fetch them periodically — there is a tunable fetch period and buffer size
- **Thread safety**: `NotificationBroadcasterSupport` uses a copy-on-write listener list; listener callbacks must be re-entrant or synchronized themselves

## Asynchronous Dispatch

`NotificationBroadcasterSupport` accepts an `Executor` constructor argument for async delivery:

```java
public class Cache extends NotificationBroadcasterSupport {
    public Cache() {
        super(Executors.newCachedThreadPool());  // listeners called on pool threads
    }
}
```

Without this, all listeners are called inline in `sendNotification()`. A slow listener blocks notification dispatch to subsequent listeners.

## Summary — Notification Design Checklist

- [ ] Extend `NotificationBroadcasterSupport` or implement `NotificationEmitter`
- [ ] Override `getNotificationInfo()` to document notification types
- [ ] Use `AtomicLong` for sequence number
- [ ] Define notification type strings as public constants
- [ ] Use `AttributeChangeNotification` for attribute-change events
- [ ] Provide an `Executor` if listeners may be slow
- [ ] Document `userData` payload type in `MBeanNotificationInfo` description
