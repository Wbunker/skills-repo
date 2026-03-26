# Ionic 4 — Native Plugins (Capacitor & Cordova)

## Capacitor vs Cordova in v4

| | Capacitor | Cordova |
|---|-----------|---------|
| Introduced | Ionic v4 era | Ionic v1–v3 |
| Plugin format | npm packages | npm + platform install |
| TypeScript | Native TS support | Via @ionic-native wrappers |
| Web support | First-class | Limited |
| iOS/Android project | Lives in repo | Generated on build |
| Recommendation | **Use for new v4 projects** | Legacy support |

---

## Capacitor Plugins

### Install a Capacitor plugin

```bash
npm install @capacitor/camera
npx cap sync   # copies plugin to native projects
```

### Camera

```typescript
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

async takePicture() {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: false,
    resultType: CameraResultType.Uri,  // or .Base64 or .DataUrl
    source: CameraSource.Camera        // or .Photos or .Prompt
  });

  this.imageUrl = image.webPath;  // use as <img [src]="imageUrl">
}
```

### Geolocation

```typescript
import { Geolocation } from '@capacitor/geolocation';

async getLocation() {
  const position = await Geolocation.getCurrentPosition({
    enableHighAccuracy: true,
    timeout: 10000
  });
  const { latitude, longitude } = position.coords;
}

// Watch position
const watchId = await Geolocation.watchPosition({}, (position, err) => {
  if (err) console.error(err);
  else console.log(position.coords.latitude, position.coords.longitude);
});

// Stop watching
await Geolocation.clearWatch({ id: watchId });
```

### Storage (Preferences)

```typescript
// @capacitor/preferences (called @capacitor/storage in earlier versions)
import { Preferences } from '@capacitor/preferences';

await Preferences.set({ key: 'name', value: JSON.stringify(data) });
const { value } = await Preferences.get({ key: 'name' });
const data = JSON.parse(value);
await Preferences.remove({ key: 'name' });
await Preferences.clear();
```

### Push Notifications

```typescript
import { PushNotifications } from '@capacitor/push-notifications';

async registerPush() {
  const permission = await PushNotifications.requestPermissions();
  if (permission.receive === 'granted') {
    await PushNotifications.register();
  }
}

// Listeners
PushNotifications.addListener('registration', (token) => {
  console.log('Push token:', token.value);
  // Send this token to your backend
});

PushNotifications.addListener('pushNotificationReceived', (notification) => {
  console.log('Notification received:', notification);
});

PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
  console.log('Notification tapped:', action);
});
```

### File System

```typescript
import { Filesystem, Directory, Encoding } from '@capacitor/filesystem';

// Write file
await Filesystem.writeFile({
  path: 'secrets/text.txt',
  data: 'This is a test',
  directory: Directory.Documents,
  encoding: Encoding.UTF8,
  recursive: true
});

// Read file
const result = await Filesystem.readFile({
  path: 'secrets/text.txt',
  directory: Directory.Documents,
  encoding: Encoding.UTF8
});
console.log(result.data);
```

### Network

```typescript
import { Network } from '@capacitor/network';

const status = await Network.getStatus();
console.log('Online:', status.connected);
console.log('Connection type:', status.connectionType); // wifi, cellular, none

Network.addListener('networkStatusChange', (status) => {
  console.log('Network changed:', status.connected);
});
```

### Device Info

```typescript
import { Device } from '@capacitor/device';

const info = await Device.getInfo();
console.log(info.platform);      // 'ios', 'android', 'web'
console.log(info.model);         // device model name
console.log(info.operatingSystem);
console.log(info.osVersion);

const battery = await Device.getBatteryInfo();
console.log(battery.batteryLevel, battery.isCharging);
```

### App

```typescript
import { App } from '@capacitor/app';

// Listen for back button (Android)
App.addListener('backButton', ({ canGoBack }) => {
  if (!canGoBack) {
    App.exitApp();
  } else {
    window.history.back();
  }
});

// App state (foreground/background)
App.addListener('appStateChange', ({ isActive }) => {
  console.log('App active:', isActive);
});
```

---

## Cordova + @ionic-native Wrappers

For projects still using Cordova, `@ionic-native` provides Angular-friendly wrappers with TypeScript types.

### Install a Cordova plugin

```bash
ionic cordova plugin add cordova-plugin-camera
npm install @ionic-native/camera
```

### Add to AppModule

```typescript
import { Camera } from '@ionic-native/camera/ngx';

@NgModule({
  providers: [Camera]
})
export class AppModule {}
```

### Use in a component

```typescript
import { Camera, CameraOptions } from '@ionic-native/camera/ngx';

constructor(private camera: Camera) {}

async takePicture() {
  const options: CameraOptions = {
    quality: 100,
    destinationType: this.camera.DestinationType.DATA_URL,
    encodingType: this.camera.EncodingType.JPEG,
    mediaType: this.camera.MediaType.PICTURE
  };
  const imageData = await this.camera.getPicture(options);
  this.imgSrc = 'data:image/jpeg;base64,' + imageData;
}
```

### Common @ionic-native plugins

| Plugin | npm | Cordova plugin |
|--------|-----|---------------|
| Camera | `@ionic-native/camera` | `cordova-plugin-camera` |
| Geolocation | `@ionic-native/geolocation` | `cordova-plugin-geolocation` |
| File | `@ionic-native/file` | `cordova-plugin-file` |
| Storage | `@ionic-native/sqlite` | `cordova-sqlite-storage` |
| Push | `@ionic-native/push` | `phonegap-plugin-push` |
| InAppBrowser | `@ionic-native/in-app-browser` | `cordova-plugin-inappbrowser` |
| StatusBar | `@ionic-native/status-bar` | `cordova-plugin-statusbar` |
| SplashScreen | `@ionic-native/splash-screen` | `cordova-plugin-splashscreen` |
| Haptics | `@ionic-native/vibration` | `cordova-plugin-vibration` |
| Barcode Scanner | `@ionic-native/barcode-scanner` | `phonegap-plugin-barcodescanner` |

---

## Platform Guards for Native Code

Always guard native calls — some plugins fail on web:

```typescript
import { Platform } from '@ionic/angular';

constructor(private platform: Platform) {}

async takePicture() {
  if (this.platform.is('capacitor')) {
    // Capacitor native
    const image = await Camera.getPhoto({...});
  } else {
    // Web fallback — use file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.click();
  }
}
```

---

## Adding iOS Permissions (Info.plist)

After adding native plugins, update iOS permissions in Xcode:
- Camera: `NSCameraUsageDescription`
- Photo Library: `NSPhotoLibraryUsageDescription`
- Location: `NSLocationWhenInUseUsageDescription`

Or in `ios/App/App/Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to let you take profile photos.</string>
```

## Adding Android Permissions (AndroidManifest.xml)

Most Capacitor plugins handle this automatically via `npx cap sync`. For manual additions:
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
```
