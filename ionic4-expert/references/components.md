# Ionic 4 — UI Components

## IonButton

```html
<!-- Basic -->
<ion-button>Click Me</ion-button>

<!-- Variants -->
<ion-button fill="solid">Solid (default)</ion-button>
<ion-button fill="outline">Outline</ion-button>
<ion-button fill="clear">Clear (text only)</ion-button>

<!-- Colors -->
<ion-button color="primary">Primary</ion-button>
<ion-button color="secondary">Secondary</ion-button>
<ion-button color="danger">Danger</ion-button>
<ion-button color="light">Light</ion-button>
<ion-button color="dark">Dark</ion-button>

<!-- Sizes -->
<ion-button size="small">Small</ion-button>
<ion-button size="default">Default</ion-button>
<ion-button size="large">Large</ion-button>

<!-- With icon -->
<ion-button>
  <ion-icon slot="start" name="star"></ion-icon>
  Favorite
</ion-button>
<ion-button>
  <ion-icon slot="icon-only" name="share"></ion-icon>
</ion-button>

<!-- Expand to full width -->
<ion-button expand="block">Block Button</ion-button>
<ion-button expand="full">Full Button (no margin)</ion-button>

<!-- Disabled, loading state -->
<ion-button [disabled]="isLoading">Submit</ion-button>
```

---

## IonIcon

Ionic uses the [Ionicons](https://ionic.io/ionicons) icon set (included by default).

```html
<ion-icon name="heart"></ion-icon>
<ion-icon name="heart-outline"></ion-icon>   <!-- outline variant -->
<ion-icon name="heart-sharp"></ion-icon>     <!-- sharp variant -->

<!-- Platform-specific icons -->
<ion-icon ios="logo-apple" md="logo-android"></ion-icon>

<!-- Sizing -->
<ion-icon name="star" size="small"></ion-icon>
<ion-icon name="star" size="large"></ion-icon>

<!-- Custom SVG -->
<ion-icon src="/assets/icon/custom.svg"></ion-icon>
```

---

## IonList & IonItem

```html
<ion-list>
  <ion-item>
    <ion-label>Simple Item</ion-label>
  </ion-item>

  <!-- With icon -->
  <ion-item>
    <ion-icon name="person" slot="start"></ion-icon>
    <ion-label>With Icon</ion-label>
  </ion-item>

  <!-- Clickable / navigable -->
  <ion-item button (click)="doSomething()" detail="true">
    <ion-label>Tappable</ion-label>
  </ion-item>

  <!-- With routerLink -->
  <ion-item [routerLink]="['/detail', item.id]" detail>
    <ion-label>{{ item.name }}</ion-label>
  </ion-item>

  <!-- With secondary action -->
  <ion-item>
    <ion-label>Item with Badge</ion-label>
    <ion-badge slot="end" color="danger">3</ion-badge>
  </ion-item>

  <!-- Item with note/subtext -->
  <ion-item>
    <ion-label>
      <h2>Primary text</h2>
      <h3>Secondary text</h3>
      <p>Tertiary text (smaller, gray)</p>
    </ion-label>
  </ion-item>
</ion-list>

<!-- Inset list (rounded corners, margins) -->
<ion-list lines="inset">...</ion-list>
<ion-list lines="none">...</ion-list>   <!-- no divider lines -->

<!-- List with header -->
<ion-list-header>
  <ion-label>Section Title</ion-label>
</ion-list-header>
```

### IonItemSliding (Swipe Actions)

```html
<ion-list>
  <ion-item-sliding *ngFor="let item of items">
    <ion-item>
      <ion-label>{{ item.title }}</ion-label>
    </ion-item>

    <ion-item-options side="end">
      <ion-item-option color="danger" (click)="delete(item)">
        <ion-icon slot="icon-only" name="trash"></ion-icon>
      </ion-item-option>
    </ion-item-options>

    <ion-item-options side="start">
      <ion-item-option color="primary" (click)="favorite(item)">
        <ion-icon slot="icon-only" name="heart"></ion-icon>
      </ion-item-option>
    </ion-item-options>
  </ion-item-sliding>
</ion-list>
```

---

## Form Inputs

```html
<!-- Text input -->
<ion-item>
  <ion-label position="floating">Email</ion-label>
  <ion-input type="email" [(ngModel)]="email" required></ion-input>
</ion-item>

<!-- label positions: "fixed", "floating", "stacked" -->

<!-- Password -->
<ion-item>
  <ion-label position="floating">Password</ion-label>
  <ion-input type="password" [(ngModel)]="password"></ion-input>
</ion-item>

<!-- Textarea -->
<ion-item>
  <ion-label position="floating">Notes</ion-label>
  <ion-textarea [(ngModel)]="notes" rows="4"></ion-textarea>
</ion-item>

<!-- Select -->
<ion-item>
  <ion-label>Country</ion-label>
  <ion-select [(ngModel)]="country" interface="popover">
    <ion-select-option value="us">United States</ion-select-option>
    <ion-select-option value="uk">United Kingdom</ion-select-option>
  </ion-select>
</ion-item>
<!-- interface: "alert" (default), "popover", "action-sheet" -->

<!-- Toggle -->
<ion-item>
  <ion-label>Notifications</ion-label>
  <ion-toggle [(ngModel)]="notificationsEnabled" slot="end"></ion-toggle>
</ion-item>

<!-- Checkbox -->
<ion-item>
  <ion-label>Accept Terms</ion-label>
  <ion-checkbox [(ngModel)]="accepted" slot="start"></ion-checkbox>
</ion-item>

<!-- Range slider -->
<ion-item>
  <ion-label>Volume</ion-label>
  <ion-range [(ngModel)]="volume" min="0" max="100" step="10">
    <ion-icon size="small" slot="start" name="volume-low"></ion-icon>
    <ion-icon slot="end" name="volume-high"></ion-icon>
  </ion-range>
</ion-item>

<!-- DateTime picker -->
<ion-item>
  <ion-label>Date</ion-label>
  <ion-datetime [(ngModel)]="date" display-format="MMM DD, YYYY"
                picker-format="YYYY MM DD"></ion-datetime>
</ion-item>
```

---

## IonCard

```html
<ion-card>
  <ion-card-header>
    <ion-card-subtitle>Card Subtitle</ion-card-subtitle>
    <ion-card-title>Card Title</ion-card-title>
  </ion-card-header>

  <ion-card-content>
    Card body text goes here.
  </ion-card-content>
</ion-card>

<!-- Card with image -->
<ion-card>
  <img src="https://example.com/image.jpg" alt="Card image"/>
  <ion-card-header>
    <ion-card-title>My Card</ion-card-title>
  </ion-card-header>
  <ion-card-content>Description text.</ion-card-content>
</ion-card>

<!-- Clickable card -->
<ion-card button (click)="openDetail()">
  ...
</ion-card>
```

---

## IonSearchbar

```html
<ion-searchbar
  [(ngModel)]="searchTerm"
  (ionChange)="onSearch($event)"
  (ionInput)="onInput($event)"
  placeholder="Search..."
  animated
  show-cancel-button="focus">
</ion-searchbar>
```

---

## IonSegment

Tabbed filter buttons within a page (not navigation):

```html
<ion-segment [(ngModel)]="selectedSegment" (ionChange)="segmentChanged($event)">
  <ion-segment-button value="all">
    <ion-label>All</ion-label>
  </ion-segment-button>
  <ion-segment-button value="active">
    <ion-label>Active</ion-label>
  </ion-segment-button>
  <ion-segment-button value="closed">
    <ion-label>Closed</ion-label>
  </ion-segment-button>
</ion-segment>
```

---

## IonFab (Floating Action Button)

```html
<ion-content>
  <ion-fab vertical="bottom" horizontal="end" slot="fixed">
    <ion-fab-button (click)="add()">
      <ion-icon name="add"></ion-icon>
    </ion-fab-button>
  </ion-fab>
</ion-content>
```

`slot="fixed"` is required so the FAB stays fixed in the content area (doesn't scroll).

### Speed dial (FAB list)

```html
<ion-fab vertical="bottom" horizontal="end" slot="fixed">
  <ion-fab-button>
    <ion-icon name="share"></ion-icon>
  </ion-fab-button>
  <ion-fab-list side="top">
    <ion-fab-button (click)="shareTwitter()">
      <ion-icon name="logo-twitter"></ion-icon>
    </ion-fab-button>
    <ion-fab-button (click)="shareFacebook()">
      <ion-icon name="logo-facebook"></ion-icon>
    </ion-fab-button>
  </ion-fab-list>
</ion-fab>
```

---

## IonInfiniteScroll

```html
<ion-content>
  <ion-list>
    <ion-item *ngFor="let item of items">{{ item }}</ion-item>
  </ion-list>

  <ion-infinite-scroll threshold="100px" (ionInfinite)="loadMore($event)">
    <ion-infinite-scroll-content
      loadingSpinner="bubbles"
      loadingText="Loading more...">
    </ion-infinite-scroll-content>
  </ion-infinite-scroll>
</ion-content>
```

```typescript
async loadMore(event: any) {
  await this.fetchNextPage();
  event.target.complete();                    // signal done loading
  if (this.allLoaded) {
    event.target.disabled = true;             // no more data
  }
}
```

---

## IonRefresher (Pull to Refresh)

```html
<ion-content>
  <ion-refresher slot="fixed" (ionRefresh)="doRefresh($event)">
    <ion-refresher-content></ion-refresher-content>
  </ion-refresher>

  <!-- content -->
</ion-content>
```

```typescript
async doRefresh(event: any) {
  await this.loadData();
  event.target.complete();
}
```

---

## IonSlides (Swiper/Carousel)

```html
<ion-slides pager="true" [options]="slideOpts">
  <ion-slide>
    <h1>Slide 1</h1>
  </ion-slide>
  <ion-slide>
    <h1>Slide 2</h1>
  </ion-slide>
</ion-slides>
```

```typescript
slideOpts = {
  initialSlide: 0,
  speed: 400,
  autoplay: { delay: 3000 }
};

@ViewChild('slides', { static: false }) slides: IonSlides;
this.slides.slideNext();
this.slides.slidePrev();
this.slides.getActiveIndex().then(i => console.log(i));
```

Note: `ion-slides` wraps Swiper.js. In Ionic v6+, it was replaced by direct Swiper.js usage — but in v4 `ion-slides` is the correct approach.

---

## IonVirtualScroll (Large Lists)

Renders only visible items for performance:

```html
<ion-virtual-scroll [items]="largeList" approxItemHeight="50px">
  <ion-item *virtualItem="let item">
    {{ item.name }}
  </ion-item>
</ion-virtual-scroll>
```
