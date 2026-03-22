# Web Capabilities (Project Fugu)

Modern browser APIs that give web apps native-like capabilities.
Docs: `https://developer.chrome.com/docs/capabilities`
Status tracker: `https://fugu-tracker.web.app`

## File System Access API (Chrome 86+)

Read and write files on the user's local file system.
Docs: `https://developer.chrome.com/articles/file-system-access`

```js
// Open file picker
const [fileHandle] = await window.showOpenFilePicker({
  types: [{ description: 'Text', accept: { 'text/plain': ['.txt'] } }],
  multiple: false,
  excludeAcceptAllOption: false,
});

// Read file
const file = await fileHandle.getFile();
const text = await file.text();

// Open save dialog
const saveHandle = await window.showSaveFilePicker({
  suggestedName: 'output.txt',
  types: [{ description: 'Text', accept: { 'text/plain': ['.txt'] } }],
});

// Write file
const writable = await saveHandle.createWritable();
await writable.write('Hello, world!');
await writable.close();

// Open directory
const dirHandle = await window.showDirectoryPicker({ mode: 'readwrite' });
for await (const [name, handle] of dirHandle) {
  console.log(name, handle.kind); // 'file' or 'directory'
}

// Read a file from directory
const fh = await dirHandle.getFileHandle('notes.txt');
const content = await (await fh.getFile()).text();

// Create/overwrite a file in directory
const newFh = await dirHandle.getFileHandle('output.txt', { create: true });
const w = await newFh.createWritable();
await w.write('data');
await w.close();

// FileSystemWritableFileStream methods
await writable.write(data);                     // string, BufferSource, Blob, or WriteParams
await writable.write({ type: 'write', position: 0, data: 'hello' });
await writable.seek(offset);
await writable.truncate(size);
```

**Browser support:** Chrome 86+, Firefox 111+ (partial), Safari 15.2+

---

## Web Share API

Share content using the OS native share dialog.

```js
// Check support
if (navigator.share) {
  await navigator.share({
    title: 'Check this out',
    text: 'Interesting article',
    url: 'https://example.com',
    files: [file],  // File objects
  });
}

// Check what can be shared
if (navigator.canShare({ files: [file] })) {
  await navigator.share({ files: [file] });
}
```

Requires a user gesture. HTTPS only.

---

## Badging API

Show a badge on the app icon (PWA / installed app).

```js
await navigator.setAppBadge();           // dot badge
await navigator.setAppBadge(42);         // numbered badge
await navigator.clearAppBadge();
```

---

## Web Bluetooth (Chrome 56+)

Connect to BLE devices.

```js
const device = await navigator.bluetooth.requestDevice({
  filters: [{ services: ['battery_service'] }],
  // or: acceptAllDevices: true, optionalServices: ['battery_service']
});

const server = await device.gatt.connect();
const service = await server.getPrimaryService('battery_service');
const characteristic = await service.getCharacteristic('battery_level');
const value = await characteristic.readValue();
console.log(value.getUint8(0)); // battery %

// Listen for notifications
await characteristic.startNotifications();
characteristic.addEventListener('characteristicvaluechanged', e => {
  console.log(e.target.value.getUint8(0));
});
```

---

## WebHID (Chrome 89+)

Access Human Interface Devices (gamepads, special keyboards, etc.)

```js
const [device] = await navigator.hid.requestDevice({
  filters: [{ vendorId: 0x057e }]  // Nintendo
});
await device.open();
device.addEventListener('inputreport', e => {
  const { data, device, reportId } = e;
});
await device.sendReport(reportId, data);
await device.close();
```

---

## Web Serial (Chrome 89+)

Communicate with serial devices (Arduino, sensors, etc.)

```js
const port = await navigator.serial.requestPort();
await port.open({ baudRate: 9600 });

const reader = port.readable.getReader();
const { value, done } = await reader.read();
reader.releaseLock();

const writer = port.writable.getWriter();
await writer.write(new TextEncoder().encode('hello\n'));
writer.releaseLock();

await port.close();
```

---

## WebUSB (Chrome 61+)

Direct USB device access from the browser.

```js
const device = await navigator.usb.requestDevice({ filters: [{ vendorId: 0x2341 }] });
await device.open();
await device.selectConfiguration(1);
await device.claimInterface(0);

const result = await device.transferIn(1, 64);  // endpoint, bytes
console.log(new TextDecoder().decode(result.data));

await device.transferOut(1, new TextEncoder().encode('data'));
await device.close();
```

---

## Window Management API (Chrome 100+)

Multi-screen window placement.

```js
const screenDetails = await window.getScreenDetails();
console.log(screenDetails.screens);  // array of ScreenDetailed
console.log(screenDetails.currentScreen);

// Place window on second screen
const screen2 = screenDetails.screens[1];
await window.moveTo(screen2.availLeft, screen2.availTop);
```

---

## Local Font Access API (Chrome 103+)

Query installed system fonts.

```js
const fonts = await window.queryLocalFonts();
for (const font of fonts) {
  console.log(font.family, font.style, font.fullName, font.postscriptName);
  const blob = await font.blob();  // get raw font data
}

// Filter
const monoFonts = await window.queryLocalFonts({ postscriptNames: ['Courier-Bold'] });
```

---

## Screen Wake Lock API (Chrome 84+)

Prevent screen from dimming/locking.

```js
let wakeLock = null;
try {
  wakeLock = await navigator.wakeLock.request('screen');
  wakeLock.addEventListener('release', () => console.log('Wake lock released'));
} catch (err) {
  console.error(err);
}

// Release manually
await wakeLock.release();
wakeLock = null;
```

---

## Gamepad API

```js
window.addEventListener('gamepadconnected', e => {
  console.log(e.gamepad.id, e.gamepad.buttons.length, e.gamepad.axes.length);
});

// Poll (must poll — no change events for axes)
function gameLoop() {
  const gamepads = navigator.getGamepads();
  for (const gp of gamepads) {
    if (!gp) continue;
    // gp.buttons[0].pressed, gp.axes[0] (-1 to 1)
  }
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

---

## Feature Detection Pattern

```js
const supported = {
  fileSystem: 'showOpenFilePicker' in window,
  webShare: 'share' in navigator,
  webBluetooth: 'bluetooth' in navigator,
  webHID: 'hid' in navigator,
  webSerial: 'serial' in navigator,
  webUSB: 'usb' in navigator,
  badging: 'setAppBadge' in navigator,
  wakeLock: 'wakeLock' in navigator,
  localFonts: 'queryLocalFonts' in window,
  windowManagement: 'getScreenDetails' in window,
};
```

Most APIs require **HTTPS** and a **user gesture** to trigger the permission prompt.
