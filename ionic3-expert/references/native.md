# Ionic 3 — Native Plugins

Ionic 3 uses **Cordova** as the native runtime. **Capacitor did not exist in Ionic 3** (it was introduced with Ionic 4).

Native functionality comes from Cordova plugins, accessed via `@ionic-native` TypeScript wrappers.

---

## Architecture

```
┌────────────────────────────────────┐
│           Ionic 3 App              │
│  TypeScript / Angular              │
│  @ionic-native wrapper             │ ← inject like any Angular service
├────────────────────────────────────┤
│  Cordova JavaScript bridge         │ ← cordova.js
├────────────────────────────────────┤
│  Cordova plugin (native code)      │ ← installed in /plugins
├────────────────────────────────────┤
│  iOS / Android platform SDKs       │
└────────────────────────────────────┘
```

---

## Installing a Native Plugin

Every plugin requires two steps:

```bash
# 1. Install the Cordova plugin (native code)
ionic cordova plugin add <cordova-plugin-name>

# 2. Install the @ionic-native TypeScript wrapper
npm install --save @ionic-native/<plugin-name>@4
```

Always install `@ionic-native` at version `@4` for Ionic 3 (v5 packages target Ionic 4+).

### Register in NgModule

Add the @ionic-native service to `providers` in `app.module.ts`:

```typescript
import { Camera } from '@ionic-native/camera';
import { Geolocation } from '@ionic-native/geolocation';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

@NgModule({
  ...
  providers: [
    Camera,
    Geolocation,
    StatusBar,
    SplashScreen,
    // ... other native services
  ]
})
export class AppModule {}
```

Then inject via constructor in any component or service:

```typescript
constructor(private camera: Camera) {}
```

---

## Camera

```bash
ionic cordova plugin add cordova-plugin-camera
npm install --save @ionic-native/camera@4
```

```typescript
import { Camera, CameraOptions } from '@ionic-native/camera';

constructor(private camera: Camera) {}

takePicture() {
  const options: CameraOptions = {
    quality: 90,
    destinationType: this.camera.DestinationType.FILE_URI,
    encodingType: this.camera.EncodingType.JPEG,
    mediaType: this.camera.MediaType.PICTURE,
    sourceType: this.camera.PictureSourceType.CAMERA,  // or PHOTOLIBRARY
    allowEdit: false,
    correctOrientation: true
  };

  this.camera.getPicture(options).then((imageData) => {
    // imageData is a FILE_URI like "file:///storage/emulated/..."
    // or base64 string if DestinationType.DATA_URL
    const imageUrl = imageData;
  }).catch((err) => {
    console.error('Camera error:', err);
  });
}

// Open photo library instead of camera
pickFromLibrary() {
  const options: CameraOptions = {
    destinationType: this.camera.DestinationType.DATA_URL,
    sourceType: this.camera.PictureSourceType.PHOTOLIBRARY
  };
  this.camera.getPicture(options).then((base64) => {
    this.imageStr = 'data:image/jpeg;base64,' + base64;
  });
}

// Clean up temp files after use
cleanup() {
  this.camera.cleanup();
}
```

**iOS:** Add to `config.xml`:
```xml
<config-file parent="NSPhotoLibraryUsageDescription" platform="ios" target="*-Info.plist">
  <string>Access photo library</string>
</config-file>
<config-file parent="NSCameraUsageDescription" platform="ios" target="*-Info.plist">
  <string>Take photos</string>
</config-file>
```

---

## Geolocation

```bash
ionic cordova plugin add cordova-plugin-geolocation --variable GEOLOCATION_USAGE_DESCRIPTION="To locate you"
npm install --save @ionic-native/geolocation@4
```

```typescript
import { Geolocation, Geoposition } from '@ionic-native/geolocation';
import { Subscription } from 'rxjs/Subscription';

constructor(private geolocation: Geolocation) {}

getCurrentLocation() {
  this.geolocation.getCurrentPosition({
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0
  }).then((resp: Geoposition) => {
    console.log('Latitude:', resp.coords.latitude);
    console.log('Longitude:', resp.coords.longitude);
    console.log('Accuracy (m):', resp.coords.accuracy);
  }).catch((error) => {
    console.error('Error getting location', error);
  });
}

// Watch position
watchSub: Subscription;

startWatching() {
  this.watchSub = this.geolocation.watchPosition({
    enableHighAccuracy: true
  }).filter(p => p.coords !== undefined)
    .subscribe((position: Geoposition) => {
      console.log(position.coords.latitude, position.coords.longitude);
    });
}

stopWatching() {
  if (this.watchSub) this.watchSub.unsubscribe();
}
```

---

## Ionic Storage

Ionic Storage is NOT a Cordova plugin — it's a JavaScript library layering IndexedDB / WebSQL / LocalStorage with optional SQLite via a Cordova plugin.

```bash
npm install --save @ionic/storage@2
# Optional: for SQLite on device (preferred over WebSQL):
ionic cordova plugin add cordova-sqlite-storage
```

### Setup in NgModule

```typescript
import { IonicStorageModule } from '@ionic/storage';

@NgModule({
  imports: [
    IonicStorageModule.forRoot({
      name: '__myapp',
      driverOrder: ['sqlite', 'indexeddb', 'websql', 'localstorage']
    })
  ]
})
export class AppModule {}
```

### Usage in a Service

```typescript
import { Storage } from '@ionic/storage';

@Injectable()
export class StorageService {
  constructor(private storage: Storage) {}

  // Set a value
  set(key: string, value: any): Promise<any> {
    return this.storage.set(key, value);
  }

  // Get a value
  get(key: string): Promise<any> {
    return this.storage.get(key);
  }

  // Remove a key
  remove(key: string): Promise<any> {
    return this.storage.remove(key);
  }

  // Clear all data
  clear(): Promise<void> {
    return this.storage.clear();
  }

  // Get all keys
  keys(): Promise<string[]> {
    return this.storage.keys();
  }

  // Iterate over all key/value pairs
  forEach(iteratorCallback: (value, key, index) => void): Promise<void> {
    return this.storage.forEach(iteratorCallback);
  }
}
```

### Usage in a Component

```typescript
import { Storage } from '@ionic/storage';

constructor(private storage: Storage) {}

async saveUser(user: any) {
  await this.storage.set('user', JSON.stringify(user));
}

async loadUser() {
  const raw = await this.storage.get('user');
  return raw ? JSON.parse(raw) : null;
}
```

**Note:** In Ionic Storage v2 (used with Ionic 3), `ready()` returns a Promise. The storage is automatically initialized, but you can wait for it:

```typescript
this.storage.ready().then(() => {
  this.storage.get('key').then(val => console.log(val));
});
```

---

## StatusBar

```bash
ionic cordova plugin add cordova-plugin-statusbar
npm install --save @ionic-native/status-bar@4
```

```typescript
import { StatusBar } from '@ionic-native/status-bar';

constructor(private statusBar: StatusBar) {}

platform.ready().then(() => {
  this.statusBar.styleDefault();          // dark text on light background
  this.statusBar.styleLightContent();     // light text on dark background
  this.statusBar.styleBlackOpaque();      // black background with light content
  this.statusBar.styleBlackTranslucent(); // translucent black with light content

  this.statusBar.overlaysWebView(false);  // don't overlap content (required on iOS for color changes)
  this.statusBar.overlaysWebView(true);   // overlap content (fullscreen feel)

  this.statusBar.backgroundColorByName('white');
  this.statusBar.backgroundColorByHexString('#ffffff');

  this.statusBar.hide();
  this.statusBar.show();

  console.log('Visible:', this.statusBar.isVisible);
});
```

**iOS note:** `overlaysWebView(false)` must be called before `backgroundColorByHexString()` works on iOS.

---

## SplashScreen

```bash
ionic cordova plugin add cordova-plugin-splashscreen
npm install --save @ionic-native/splash-screen@4
```

```typescript
import { SplashScreen } from '@ionic-native/splash-screen';

constructor(private splashScreen: SplashScreen) {}

platform.ready().then(() => {
  this.splashScreen.hide();
  // Or: this.splashScreen.show();
});
```

The splash screen is shown automatically at launch based on `config.xml` settings.

---

## Push Notifications

```bash
ionic cordova plugin add phonegap-plugin-push
npm install --save @ionic-native/push@4
```

```typescript
import { Push, PushObject, PushOptions } from '@ionic-native/push';

constructor(private push: Push) {}

initPush() {
  // Check/request permission
  this.push.hasPermission().then((res) => {
    if (!res.isEnabled) {
      console.log('Push permission not enabled');
    }
  });

  const options: PushOptions = {
    android: {
      senderID: 'YOUR_SENDER_ID',
      sound: true,
      vibrate: true
    },
    ios: {
      alert: 'true',
      badge: true,
      sound: 'false'
    },
    windows: {}
  };

  const pushObject: PushObject = this.push.init(options);

  // Receive a notification
  pushObject.on('notification').subscribe((notification: any) => {
    console.log('Notification received:', notification);
    console.log('Message:', notification.message);
    console.log('Title:', notification.title);
    console.log('Additional data:', notification.additionalData);

    if (notification.additionalData.foreground) {
      // App was open when notification arrived
    } else {
      // App was opened by tapping the notification
    }
  });

  // Device registered — send this token to your backend
  pushObject.on('registration').subscribe((registration: any) => {
    console.log('Device token:', registration.registrationId);
  });

  // Error handling
  pushObject.on('error').subscribe((error: any) => {
    console.error('Push error:', error);
  });
}
```

---

## File Plugin

```bash
ionic cordova plugin add cordova-plugin-file
npm install --save @ionic-native/file@4
```

```typescript
import { File } from '@ionic-native/file';

constructor(private file: File) {}

async writeFile() {
  try {
    await this.file.writeFile(
      this.file.dataDirectory,   // platform data directory
      'myfile.txt',
      'Hello World',
      { replace: true }
    );
    console.log('File written');
  } catch (err) {
    console.error(err);
  }
}

async readFile() {
  const text = await this.file.readAsText(this.file.dataDirectory, 'myfile.txt');
  console.log(text);
}
```

---

## Network Plugin

```bash
ionic cordova plugin add cordova-plugin-network-information
npm install --save @ionic-native/network@4
```

```typescript
import { Network } from '@ionic-native/network';

constructor(private network: Network) {}

checkNetwork() {
  console.log('Connection type:', this.network.type);
  // Types: wifi, 2g, 3g, 4g, cellular, none, unknown

  this.network.onConnect().subscribe(() => {
    console.log('Network connected');
  });

  this.network.onDisconnect().subscribe(() => {
    console.log('Network disconnected');
  });
}
```

---

## InAppBrowser

```bash
ionic cordova plugin add cordova-plugin-inappbrowser
npm install --save @ionic-native/in-app-browser@4
```

```typescript
import { InAppBrowser } from '@ionic-native/in-app-browser';

constructor(private iab: InAppBrowser) {}

openUrl(url: string) {
  const browser = this.iab.create(url, '_blank', {
    location: 'yes',
    clearcache: 'yes',
    hardwareback: 'yes'
  });

  browser.on('loadstop').subscribe(event => {
    console.log('Page loaded:', event.url);
  });

  browser.close();
}

// Open in system browser
openExternal(url: string) {
  this.iab.create(url, '_system');
}

// Open in app (WebView, no location bar)
openInApp(url: string) {
  this.iab.create(url, '_blank', 'location=no');
}
```

---

## Common Plugin Installation Errors

| Error | Fix |
|-------|-----|
| `Plugin not installed` at runtime | Run `ionic cordova build ios/android` — not just `ionic serve` |
| `Class 'X' not found` | Add to `providers` in `app.module.ts` |
| `NullInjectorError` | Injectable not in providers array |
| iOS permission crash | Add usage description strings to `config.xml` |
| Build fails after adding plugin | Run `ionic cordova platform rm android && ionic cordova platform add android` |

### Testing Native Plugins

Native plugins only work on a real device or emulator — they do NOT work in `ionic serve` (browser). Use `ionic cordova run android --device` for testing.

For browser testing, `@ionic-native` provides a mock/stub pattern or use `ionic-native-mocks`:

```bash
npm install --save-dev ionic-native-mocks
```
