# Ionic 3 — Overlays

All overlay controllers follow the same pattern: inject the controller, call `create()` with options, then call `present()`. Use `dismiss()` to close programmatically.

Import all controllers from `ionic-angular`.

---

## ModalController

Presents a full-screen (or near full-screen) page as an overlay.

### Presenting a Modal

```typescript
import { Component } from '@angular/core';
import { ModalController, NavParams } from 'ionic-angular';
import { ProfileModal } from '../profile-modal/profile-modal';

@Component({ templateUrl: 'home.html' })
export class HomePage {
  constructor(public modalCtrl: ModalController) {}

  openProfile() {
    const modal = this.modalCtrl.create(ProfileModal, {
      userId: 8675309,
      name: 'Alice'
    });

    // Callback when modal is dismissed
    modal.onDidDismiss((data) => {
      console.log('Modal dismissed with:', data);
    });

    modal.present();
  }
}
```

### Modal Component

```typescript
import { Component } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';

@Component({ templateUrl: 'profile-modal.html' })
export class ProfileModal {
  userId: number;

  constructor(
    public viewCtrl: ViewController,
    public navParams: NavParams
  ) {
    this.userId = navParams.get('userId');
  }

  dismiss() {
    // Pass data back to presenter
    this.viewCtrl.dismiss({ saved: true, newName: 'Bob' });
  }

  cancel() {
    this.viewCtrl.dismiss();
  }
}
```

### create() Options

| Option | Type | Description |
|--------|------|-------------|
| `showBackdrop` | boolean | Show dark backdrop (default: true) |
| `enableBackdropDismiss` | boolean | Tap backdrop to dismiss (default: true) |
| `cssClass` | string | Custom CSS class(es) |
| `enterAnimation` | string | Custom enter animation name |
| `leaveAnimation` | string | Custom leave animation name |

### Registering Modal in NgModule

For eager loading, add the modal component to both `declarations` and `entryComponents` in `app.module.ts`. For lazy loading, add it to `declarations` and `entryComponents` in its own module.

---

## AlertController

Presents dialogs for information, confirmation, prompts, and radio/checkbox inputs.

### Basic Alert

```typescript
import { AlertController } from 'ionic-angular';

constructor(private alertCtrl: AlertController) {}

showAlert() {
  const alert = this.alertCtrl.create({
    title: 'Low Battery',
    subTitle: '10% of battery remaining',
    buttons: ['Dismiss']
  });
  alert.present();
}
```

### Confirmation Alert

```typescript
showConfirm() {
  const alert = this.alertCtrl.create({
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete this item?',
    buttons: [
      {
        text: 'Cancel',
        role: 'cancel',
        handler: () => {
          console.log('Cancelled');
        }
      },
      {
        text: 'Delete',
        handler: () => {
          this.deleteItem();
        }
      }
    ]
  });
  alert.present();
}
```

### Prompt Alert (Text Input)

```typescript
showPrompt() {
  const alert = this.alertCtrl.create({
    title: 'Login',
    inputs: [
      { name: 'username', placeholder: 'Username' },
      { name: 'password', placeholder: 'Password', type: 'password' }
    ],
    buttons: [
      { text: 'Cancel', role: 'cancel' },
      {
        text: 'Login',
        handler: (data) => {
          console.log('Username:', data.username);
          console.log('Password:', data.password);
          // Return false to prevent auto-dismiss
          if (!this.isValid(data)) return false;
        }
      }
    ]
  });
  alert.present();
}
```

### Radio Alert

```typescript
showRadio() {
  const alert = this.alertCtrl.create({
    title: 'Favorite Color',
    inputs: [
      { type: 'radio', label: 'Red',   value: 'red',   checked: true },
      { type: 'radio', label: 'Green', value: 'green' },
      { type: 'radio', label: 'Blue',  value: 'blue'  }
    ],
    buttons: [
      { text: 'Cancel', role: 'cancel' },
      {
        text: 'OK',
        handler: (data) => {
          console.log('Selected:', data);  // data is the value string
        }
      }
    ]
  });
  alert.present();
}
```

### Checkbox Alert

```typescript
showCheckboxes() {
  const alert = this.alertCtrl.create({
    title: 'Select Toppings',
    inputs: [
      { type: 'checkbox', label: 'Pepperoni',  value: 'pepperoni',  checked: true },
      { type: 'checkbox', label: 'Mushrooms',  value: 'mushrooms' },
      { type: 'checkbox', label: 'Extra Cheese', value: 'cheese' }
    ],
    buttons: [
      { text: 'Cancel', role: 'cancel' },
      {
        text: 'OK',
        handler: (data) => {
          console.log('Selected:', data);  // data is Array of selected values
        }
      }
    ]
  });
  alert.present();
}
```

### Alert Options Reference

| Option | Type | Description |
|--------|------|-------------|
| `title` | string | Alert title |
| `subTitle` | string | Alert subtitle (smaller text) |
| `message` | string | Body message |
| `cssClass` | string | Custom CSS class |
| `inputs` | AlertInput[] | Input fields |
| `buttons` | AlertButton[] | Action buttons |
| `enableBackdropDismiss` | boolean | Tap backdrop to dismiss (default: true) |

**AlertInput** properties: `type`, `name`, `placeholder`, `value`, `label`, `checked`, `id`

**AlertButton** properties: `text`, `handler`, `cssClass`, `role` (`'cancel'`)

### Handler Return false Pattern

Return `false` from a button handler to prevent automatic dismissal:

```typescript
handler: (data) => {
  if (!this.validate(data)) {
    return false;  // keeps alert open
  }
  // alert auto-dismisses if you don't return false
}
```

---

## ToastController

Brief, non-blocking notification messages.

```typescript
import { ToastController } from 'ionic-angular';

constructor(private toastCtrl: ToastController) {}

showToast() {
  const toast = this.toastCtrl.create({
    message: 'Item saved successfully',
    duration: 3000,
    position: 'bottom',
    showCloseButton: true,
    closeButtonText: 'OK'
  });

  toast.onDidDismiss(() => {
    console.log('Toast dismissed');
  });

  toast.present();
}
```

### create() Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `message` | string | — | Notification text |
| `duration` | number | — | Auto-dismiss time in ms (no auto-dismiss if omitted) |
| `position` | string | `bottom` | `top`, `middle`, `bottom` |
| `cssClass` | string | — | Custom CSS class |
| `showCloseButton` | boolean | `false` | Show a close button |
| `closeButtonText` | string | `Close` | Close button label |
| `dismissOnPageChange` | boolean | `false` | Auto-dismiss on navigation |

### Dismiss Programmatically

```typescript
const toast = this.toastCtrl.create({ message: 'Loading...' });
toast.present();

// Later:
toast.dismiss();
```

---

## ActionSheetController

Presents a set of action buttons sliding up from the bottom.

```typescript
import { ActionSheetController } from 'ionic-angular';

constructor(private actionSheetCtrl: ActionSheetController) {}

presentActionSheet() {
  const actionSheet = this.actionSheetCtrl.create({
    title: 'Options',
    subTitle: 'Choose an action',
    cssClass: 'my-action-sheet',
    buttons: [
      {
        text: 'Delete',
        role: 'destructive',   // red styling on iOS
        icon: 'trash',
        handler: () => {
          console.log('Delete clicked');
        }
      },
      {
        text: 'Share',
        icon: 'share',
        handler: () => {
          console.log('Share clicked');
        }
      },
      {
        text: 'Cancel',
        role: 'cancel',        // always shown last, fires on backdrop tap
        handler: () => {
          console.log('Cancelled');
        }
      }
    ]
  });
  actionSheet.present();
}
```

### create() Options

| Option | Type | Description |
|--------|------|-------------|
| `title` | string | Sheet title |
| `subTitle` | string | Sheet subtitle |
| `cssClass` | string | Custom CSS class |
| `enableBackdropDismiss` | boolean | Allow backdrop tap to dismiss (default: true) |
| `buttons` | ActionSheetButton[] | Array of buttons |

**ActionSheetButton** properties:

| Property | Type | Description |
|----------|------|-------------|
| `text` | string | Button label |
| `icon` | string | Ionicon name |
| `handler` | function | Click callback |
| `cssClass` | string | Custom class |
| `role` | string | `cancel` or `destructive` |

**Roles:**
- `cancel` — styled as cancel, always at bottom, fires if backdrop tapped
- `destructive` — styled in red (iOS), should be first in list

---

## LoadingController

Blocking overlay with spinner to indicate background work.

```typescript
import { LoadingController } from 'ionic-angular';

constructor(private loadingCtrl: LoadingController) {}

// Simple usage
async loadData() {
  const loading = this.loadingCtrl.create({
    content: 'Please wait...',
    spinner: 'crescent'
  });
  loading.present();

  try {
    const data = await this.apiService.getData().toPromise();
    this.items = data;
  } finally {
    loading.dismiss();
  }
}

// With duration auto-dismiss
showBriefly() {
  const loading = this.loadingCtrl.create({
    content: 'Saving...',
    duration: 2000   // auto-dismiss after 2 seconds
  });
  loading.present();
}
```

### create() Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `content` | string | — | HTML content / message |
| `spinner` | string | platform | Spinner name: `ios`, `ios-small`, `bubbles`, `circles`, `crescent`, `dots`, `lines`, `hide` |
| `showBackdrop` | boolean | `true` | Show dark backdrop |
| `enableBackdropDismiss` | boolean | `false` | Allow backdrop tap to dismiss |
| `dismissOnPageChange` | boolean | `false` | Dismiss on navigation |
| `duration` | number | — | Auto-dismiss after ms |
| `cssClass` | string | — | Custom CSS class |

**Important:** After calling `dismiss()`, the Loading instance cannot be reused. Create a new one for each use.

### With onDidDismiss

```typescript
loading.onDidDismiss(() => {
  console.log('Loading overlay closed');
});
```

---

## PopoverController

Contextual popup that positions relative to a clicked element.

### Presenting a Popover

```typescript
import { PopoverController } from 'ionic-angular';
import { PopoverPage } from './popover/popover';

constructor(private popoverCtrl: PopoverController) {}

presentPopover(event: Event) {
  const popover = this.popoverCtrl.create(PopoverPage, {
    someData: 'value'
  });

  // Pass the event to position the popover near the clicked element
  popover.present({ ev: event });

  popover.onDidDismiss((data) => {
    console.log('Popover data:', data);
  });
}
```

In the template:

```html
<button ion-button (click)="presentPopover($event)">
  <ion-icon name="more"></ion-icon>
</button>
```

### Popover Content Component

```typescript
import { Component } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';

@Component({
  template: `
    <ion-list>
      <button ion-item (click)="selectOption('edit')">Edit</button>
      <button ion-item (click)="selectOption('delete')">Delete</button>
    </ion-list>
  `
})
export class PopoverPage {
  constructor(
    public viewCtrl: ViewController,
    public navParams: NavParams
  ) {}

  selectOption(option: string) {
    this.viewCtrl.dismiss({ option });
  }
}
```

### create() Options

| Option | Type | Description |
|--------|------|-------------|
| `cssClass` | string | Custom CSS class |
| `showBackdrop` | boolean | Show backdrop (default: true) |
| `enableBackdropDismiss` | boolean | Tap backdrop to dismiss (default: true) |

---

## Common Patterns

### Async/Await with Overlays

```typescript
async deleteItem(item: any) {
  const confirm = await new Promise<boolean>((resolve) => {
    const alert = this.alertCtrl.create({
      title: 'Confirm',
      message: 'Delete this item?',
      buttons: [
        { text: 'Cancel', role: 'cancel', handler: () => resolve(false) },
        { text: 'Delete', handler: () => resolve(true) }
      ]
    });
    alert.present();
  });

  if (confirm) {
    const loading = this.loadingCtrl.create({ content: 'Deleting...' });
    loading.present();
    await this.service.delete(item.id).toPromise();
    loading.dismiss();
    this.showToast('Item deleted');
  }
}
```

### Navigating After Overlay Dismiss

Do not navigate while an overlay is animating. Wait for the overlay's transition:

```typescript
const alert = this.alertCtrl.create({
  buttons: [{
    text: 'Go',
    handler: () => {
      const navTransition = alert.dismiss();
      navTransition.then(() => {
        this.navCtrl.push(NextPage);
      });
      return false;  // prevent auto-dismiss so we control timing
    }
  }]
});
alert.present();
```
