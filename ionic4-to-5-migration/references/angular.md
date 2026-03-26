# Angular-Specific Changes

## Events Service Removed

`Events` from `@ionic/angular` is gone entirely. It was a simple pub/sub bus; replace it with a shared Angular service using RxJS.

### Simple replacement with BehaviorSubject

```typescript
// Before: using Ionic Events
import { Events } from '@ionic/angular';

@Component({...})
export class PublisherComponent {
  constructor(private events: Events) {}

  doSomething() {
    this.events.publish('user:updated', { name: 'Alice' });
  }
}

@Component({...})
export class SubscriberComponent implements OnInit, OnDestroy {
  constructor(private events: Events) {}

  ngOnInit() {
    this.events.subscribe('user:updated', (data) => {
      console.log(data.name);
    });
  }

  ngOnDestroy() {
    this.events.unsubscribe('user:updated');
  }
}
```

```typescript
// After: shared service with BehaviorSubject
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserService {
  private userSubject = new BehaviorSubject<{ name: string } | null>(null);
  user$ = this.userSubject.asObservable();

  updateUser(data: { name: string }) {
    this.userSubject.next(data);
  }
}
```

```typescript
// Publisher
@Component({...})
export class PublisherComponent {
  constructor(private userService: UserService) {}

  doSomething() {
    this.userService.updateUser({ name: 'Alice' });
  }
}
```

```typescript
// Subscriber
import { Subscription } from 'rxjs';

@Component({...})
export class SubscriberComponent implements OnInit, OnDestroy {
  private sub: Subscription;

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.sub = this.userService.user$.subscribe(data => {
      if (data) console.log(data.name);
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }
}
```

### Using Subject for fire-and-forget events

If you don't need the last value on subscribe (true events, not state):

```typescript
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AppEvents {
  private walletUpdated = new Subject<number>();
  walletUpdated$ = this.walletUpdated.asObservable();

  emitWalletUpdate(amount: number) {
    this.walletUpdated.next(amount);
  }
}
```

Use `Subject` for events, `BehaviorSubject` for state that components need on subscribe.

## MenuController.swipeEnable → swipeGesture

```typescript
// Before
import { MenuController } from '@ionic/angular';

this.menuController.swipeEnable(false);
this.menuController.swipeEnable(true, 'my-menu');

// After
this.menuController.swipeGesture(false);
this.menuController.swipeGesture(true, 'my-menu');
```

## Angular 9 / Ivy

No code changes are required for Ivy. Benefits:
- Smaller bundle sizes via improved tree-shaking
- Faster compilation
- Better error messages

One cleanup: remove `entryComponents` from NgModules. Ionic overlay components (modals, popovers passed as components) no longer need to be listed there.

```typescript
// Before (required in Angular 8 and below)
@NgModule({
  declarations: [AppComponent, MyModalComponent],
  entryComponents: [MyModalComponent],  // ← remove this line
  imports: [IonicModule.forRoot()],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

```typescript
// After (Angular 9+ / Ivy)
@NgModule({
  declarations: [AppComponent, MyModalComponent],
  imports: [IonicModule.forRoot()],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

## Angular Upgrade Path

If you're also upgrading Angular (e.g., from v8 to v9 at the same time):

```bash
# 1. Update Angular
ng update @angular/cli @angular/core

# 2. Update Ionic
npm install @ionic/angular@5 @ionic/angular-toolkit@2.2.0

# 3. Run migrations
ng update @ionic/angular
```

The Angular update schematic handles most Angular-level breaking changes. Ionic-specific template changes need manual fixes (this guide covers them).

## Module Import Pattern (Unchanged)

The `IonicModule` import pattern is **unchanged** in v5:

```typescript
// app.module.ts — same as v4
import { IonicModule } from '@ionic/angular';

@NgModule({
  imports: [
    IonicModule.forRoot(),
    ...
  ]
})
export class AppModule {}
```

Lazy-loaded page modules also unchanged — still import `IonicModule` (not `.forRoot()`):
```typescript
@NgModule({
  imports: [CommonModule, FormsModule, IonicModule, HomePageRoutingModule],
  declarations: [HomePage]
})
export class HomePageModule {}
```
