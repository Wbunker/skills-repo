# Ionic 4 — Overlays (Modal, Alert, Toast, etc.)

All overlay controllers follow the same pattern: inject the controller → `create()` → `present()` → `dismiss()`.

---

## IonModal

Full-screen overlay. Good for forms, detail views, and complex interactions.

### Basic modal

```typescript
// In the page that opens the modal:
import { ModalController } from '@ionic/angular';
import { MyModalPage } from '../my-modal/my-modal.page';

constructor(private modalCtrl: ModalController) {}

async openModal() {
  const modal = await this.modalCtrl.create({
    component: MyModalPage,
    componentProps: {
      title: 'Hello',
      itemId: 42
    }
  });

  await modal.present();

  // Wait for modal to close and get return value
  const { data, role } = await modal.onWillDismiss();
  if (role === 'confirm') {
    console.log('User confirmed with:', data);
  }
}
```

### Inside the modal page

```typescript
// my-modal.page.ts
import { ModalController } from '@ionic/angular';

@Component({ ... })
export class MyModalPage {
  @Input() title: string;    // receives componentProps
  @Input() itemId: number;

  constructor(private modalCtrl: ModalController) {}

  confirm() {
    this.modalCtrl.dismiss({ result: 'some data' }, 'confirm');
  }

  cancel() {
    this.modalCtrl.dismiss(null, 'cancel');
  }
}
```

```html
<!-- my-modal.page.html -->
<ion-header>
  <ion-toolbar>
    <ion-buttons slot="start">
      <ion-button (click)="cancel()">Cancel</ion-button>
    </ion-buttons>
    <ion-title>{{ title }}</ion-title>
    <ion-buttons slot="end">
      <ion-button (click)="confirm()">Confirm</ion-button>
    </ion-buttons>
  </ion-toolbar>
</ion-header>
<ion-content>
  <!-- modal body -->
</ion-content>
```

**Important**: The modal component must be declared in a module and added to `entryComponents`:

```typescript
// If the modal page uses its own module (lazy-loaded), pass the module:
const modal = await this.modalCtrl.create({
  component: MyModalPage
});

// If NOT lazy-loaded, add to entryComponents in the page's module:
@NgModule({
  declarations: [MyPage, MyModalPage],
  entryComponents: [MyModalPage],  // required in v4
  ...
})
```

### Card-style modal (partial overlay)

```typescript
const modal = await this.modalCtrl.create({
  component: MyModalPage,
  cssClass: 'my-card-modal',
  swipeToClose: true,       // allows swipe down to dismiss
  presentingElement: this.routerOutlet.nativeEl  // needed for card presentation
});
```

```css
/* global.scss */
.my-card-modal {
  --height: 50%;
  --border-radius: 16px;
}
```

---

## IonAlert

Simple dialogs with buttons. Good for confirmations and simple prompts.

```typescript
import { AlertController } from '@ionic/angular';

constructor(private alertCtrl: AlertController) {}

async showConfirm() {
  const alert = await this.alertCtrl.create({
    header: 'Confirm Delete',
    message: 'Are you sure you want to delete this item?',
    buttons: [
      {
        text: 'Cancel',
        role: 'cancel'
      },
      {
        text: 'Delete',
        role: 'destructive',
        cssClass: 'alert-button-danger',
        handler: () => {
          this.deleteItem();
        }
      }
    ]
  });
  await alert.present();
}

// Alert with text input
async showPrompt() {
  const alert = await this.alertCtrl.create({
    header: 'Enter Name',
    inputs: [
      {
        name: 'username',
        type: 'text',
        placeholder: 'Your name'
      }
    ],
    buttons: [
      { text: 'Cancel', role: 'cancel' },
      {
        text: 'OK',
        handler: (data) => {
          console.log('Name entered:', data.username);
        }
      }
    ]
  });
  await alert.present();
}

// Alert with radio buttons
async showRadio() {
  const alert = await this.alertCtrl.create({
    header: 'Pick a color',
    inputs: [
      { type: 'radio', label: 'Red', value: 'red' },
      { type: 'radio', label: 'Blue', value: 'blue', checked: true }
    ],
    buttons: ['Cancel', 'OK']
  });
  await alert.present();
  const { data } = await alert.onWillDismiss();
  console.log('Selected:', data.values);
}
```

---

## IonToast

Brief non-intrusive messages.

```typescript
import { ToastController } from '@ionic/angular';

constructor(private toastCtrl: ToastController) {}

async showToast(message: string) {
  const toast = await this.toastCtrl.create({
    message,
    duration: 2000,           // auto-dismiss after 2 seconds
    position: 'bottom',       // 'top', 'middle', 'bottom'
    color: 'success',         // any Ionic color
    buttons: [
      {
        text: 'Undo',
        handler: () => this.undoAction()
      },
      {
        icon: 'close',
        role: 'cancel'
      }
    ]
  });
  await toast.present();
}
```

---

## IonActionSheet

Bottom sheet with a list of actions. Good for context menus.

```typescript
import { ActionSheetController } from '@ionic/angular';

constructor(private actionSheetCtrl: ActionSheetController) {}

async showActions() {
  const actionSheet = await this.actionSheetCtrl.create({
    header: 'Photo Options',
    buttons: [
      {
        text: 'Take Photo',
        icon: 'camera',
        handler: () => this.takePhoto()
      },
      {
        text: 'Choose from Library',
        icon: 'image',
        handler: () => this.pickFromLibrary()
      },
      {
        text: 'Delete',
        icon: 'trash',
        role: 'destructive',
        handler: () => this.deletePhoto()
      },
      {
        text: 'Cancel',
        icon: 'close',
        role: 'cancel'
      }
    ]
  });
  await actionSheet.present();
}
```

---

## IonLoading

Full-screen or inline loading spinner. Always `dismiss()` it when done.

```typescript
import { LoadingController } from '@ionic/angular';

constructor(private loadingCtrl: LoadingController) {}

async showLoading() {
  const loading = await this.loadingCtrl.create({
    message: 'Please wait...',
    spinner: 'bubbles',    // 'crescent', 'dots', 'lines', 'bubbles', etc.
    duration: 5000,        // optional auto-dismiss
    cssClass: 'custom-loading'
  });
  await loading.present();

  try {
    await this.doLongOperation();
  } finally {
    await loading.dismiss();
  }
}

// Pattern: helper methods
private loading: HTMLIonLoadingElement;

async presentLoading(message = 'Loading...') {
  this.loading = await this.loadingCtrl.create({ message });
  await this.loading.present();
}

async dismissLoading() {
  if (this.loading) {
    await this.loading.dismiss();
    this.loading = null;
  }
}
```

---

## IonPopover

Contextual bubble overlay — good for tooltips or small menus.

```typescript
import { PopoverController } from '@ionic/angular';
import { MyPopoverComponent } from '../my-popover/my-popover.component';

constructor(private popoverCtrl: PopoverController) {}

async showPopover(event: Event) {
  const popover = await this.popoverCtrl.create({
    component: MyPopoverComponent,
    componentProps: { items: this.menuItems },
    event,           // positions popover near the trigger element
    translucent: true
  });
  await popover.present();

  const { data } = await popover.onWillDismiss();
  if (data) this.handleSelection(data.selected);
}
```

```typescript
// my-popover.component.ts
@Component({ ... })
export class MyPopoverComponent {
  @Input() items: string[];
  constructor(private popoverCtrl: PopoverController) {}

  select(item: string) {
    this.popoverCtrl.dismiss({ selected: item });
  }
}
```

---

## Common Overlay Patterns

### Dismiss all overlays on logout

```typescript
// Useful when forcing user to login screen
async dismissAll() {
  try { await this.modalCtrl.dismiss(); } catch {}
  try { await this.alertCtrl.dismiss(); } catch {}
  try { await this.loadingCtrl.dismiss(); } catch {}
}
```

### Prevent backdrop dismiss

```typescript
const modal = await this.modalCtrl.create({
  component: MyPage,
  backdropDismiss: false   // user cannot tap outside to close
});
```
