# Ionic 3 — UI Components

## ion-button

Buttons in Ionic 3 use the `ion-button` attribute on a `<button>` element (not a standalone element like v4).

```html
<!-- Basic button -->
<button ion-button>Click Me</button>

<!-- With color -->
<button ion-button color="primary">Primary</button>
<button ion-button color="danger">Danger</button>
<button ion-button color="secondary">Secondary</button>

<!-- Sizes -->
<button ion-button large>Large</button>
<button ion-button small>Small</button>

<!-- Styles -->
<button ion-button outline>Outline</button>
<button ion-button clear>Clear (text only)</button>
<button ion-button solid>Solid (default)</button>

<!-- Full width -->
<button ion-button block>Block Button</button>
<button ion-button full>Full Width (no rounded corners)</button>

<!-- Round -->
<button ion-button round>Rounded</button>

<!-- Icon only -->
<button ion-button icon-only>
  <ion-icon name="heart"></ion-icon>
</button>

<!-- Icon + text -->
<button ion-button>
  <ion-icon name="home" item-start></ion-icon>
  Home
</button>

<!-- Disabled -->
<button ion-button [disabled]="isDisabled">Disabled</button>

<!-- FAB button -->
<button ion-button fab>
  <ion-icon name="add"></ion-icon>
</button>
```

---

## ion-icon

Uses Ionicons. In v3, set icons via `name` attribute.

```html
<ion-icon name="home"></ion-icon>
<ion-icon name="heart" color="danger"></ion-icon>

<!-- iOS / MD platform-specific icons -->
<ion-icon ios="ios-heart" md="md-heart"></ion-icon>

<!-- Sizing -->
<ion-icon name="home" large></ion-icon>
<ion-icon name="home" small></ion-icon>
```

---

## ion-list / ion-item / ion-label

```html
<ion-list>
  <!-- Basic item -->
  <ion-item>
    <ion-label>Item Text</ion-label>
  </ion-item>

  <!-- Item with icon -->
  <ion-item>
    <ion-icon name="home" item-start></ion-icon>
    <ion-label>Home</ion-label>
  </ion-item>

  <!-- Clickable item (navigates) -->
  <button ion-item (click)="openDetail(item)">
    <ion-label>{{ item.title }}</ion-label>
    <ion-icon name="arrow-forward" item-end></ion-icon>
  </button>

  <!-- Item with detail arrow (iOS style) -->
  <button ion-item detail>Detail Item</button>

  <!-- Avatar item -->
  <ion-item>
    <ion-avatar item-start>
      <img src="assets/img/avatar.jpg">
    </ion-avatar>
    <ion-label>
      <h2>Name</h2>
      <p>Subtitle text</p>
    </ion-label>
  </ion-item>

  <!-- Thumbnail item -->
  <ion-item>
    <ion-thumbnail item-start>
      <img src="assets/img/thumb.jpg">
    </ion-thumbnail>
    <ion-label>Title</ion-label>
  </ion-item>
</ion-list>
```

### ion-item Position Attributes

In v3, item start/end positioning uses attributes, not `slot`:

| Attribute | Equivalent to | Description |
|-----------|--------------|-------------|
| `item-start` | left side | Position element at start |
| `item-end` | right side | Position element at end |
| `item-left` | synonym for item-start | |
| `item-right` | synonym for item-end | |

### ion-list Attributes

```html
<ion-list no-lines>          <!-- hide dividers -->
<ion-list inset>             <!-- rounded corners (iOS style) -->
<ion-list-header>Header</ion-list-header>  <!-- list section header -->
<ion-item-divider>Divider</ion-item-divider>  <!-- divider within list -->
<ion-item-group>             <!-- group of items -->
```

---

## ion-input

```html
<!-- Text input in an item -->
<ion-item>
  <ion-label>Email</ion-label>
  <ion-input type="email" [(ngModel)]="email" placeholder="you@example.com"></ion-input>
</ion-item>

<!-- Floating label -->
<ion-item>
  <ion-label floating>Password</ion-label>
  <ion-input type="password" [(ngModel)]="password"></ion-input>
</ion-item>

<!-- Stacked label -->
<ion-item>
  <ion-label stacked>Username</ion-label>
  <ion-input [(ngModel)]="username"></ion-input>
</ion-item>

<!-- Fixed label (left-aligned, input to the right) -->
<ion-item>
  <ion-label fixed>Name</ion-label>
  <ion-input [(ngModel)]="name"></ion-input>
</ion-item>
```

### ion-label Modes

| Attribute | Description |
|-----------|-------------|
| `floating` | Label floats above input when focused/filled |
| `stacked` | Label always above the input |
| `fixed` | Label on left, input to the right |
| _(none)_ | Label inline with input |

---

## ion-select / ion-option

```html
<ion-item>
  <ion-label>Color</ion-label>
  <ion-select [(ngModel)]="selectedColor">
    <ion-option value="red">Red</ion-option>
    <ion-option value="green">Green</ion-option>
    <ion-option value="blue">Blue</ion-option>
  </ion-select>
</ion-item>

<!-- Multiple selection -->
<ion-item>
  <ion-label>Toppings</ion-label>
  <ion-select [(ngModel)]="toppings" multiple="true">
    <ion-option value="pepperoni">Pepperoni</ion-option>
    <ion-option value="mushrooms">Mushrooms</ion-option>
  </ion-select>
</ion-item>

<!-- Action sheet interface instead of alert -->
<ion-select interface="action-sheet" [(ngModel)]="fruit">
  <ion-option value="apple">Apple</ion-option>
  <ion-option value="banana">Banana</ion-option>
</ion-select>
```

| Attribute | Type | Description |
|-----------|------|-------------|
| `interface` | string | `alert` (default), `action-sheet`, `popover` |
| `multiple` | boolean | Allow multi-select |
| `placeholder` | string | Shown when nothing is selected |
| `cancelText` | string | Cancel button label |
| `okText` | string | OK button label |
| `selectOptions` | object | Options passed to the controller |

---

## ion-toggle

```html
<ion-item>
  <ion-label>Notifications</ion-label>
  <ion-toggle [(ngModel)]="notifications" color="secondary"></ion-toggle>
</ion-item>
```

---

## ion-checkbox

```html
<ion-item>
  <ion-label>Accept Terms</ion-label>
  <ion-checkbox [(ngModel)]="accepted" color="primary"></ion-checkbox>
</ion-item>
```

---

## ion-radio / ion-radio-group

```html
<ion-list radio-group [(ngModel)]="selectedPet">
  <ion-list-header>Favorite Pet</ion-list-header>
  <ion-item>
    <ion-label>Dogs</ion-label>
    <ion-radio value="dogs"></ion-radio>
  </ion-item>
  <ion-item>
    <ion-label>Cats</ion-label>
    <ion-radio value="cats"></ion-radio>
  </ion-item>
</ion-list>
```

The `radio-group` directive on `ion-list` provides the group context. Two-way binding is on the list itself.

---

## ion-range

```html
<ion-item>
  <ion-range [(ngModel)]="volume" min="0" max="100" step="1" color="secondary">
    <ion-icon range-left small name="volume-low"></ion-icon>
    <ion-icon range-right name="volume-high"></ion-icon>
  </ion-range>
</ion-item>

<!-- Dual knobs -->
<ion-range dualKnobs [(ngModel)]="priceRange" min="0" max="500" step="10">
</ion-range>
```

| Attribute | Type | Description |
|-----------|------|-------------|
| `min` | number | Minimum value |
| `max` | number | Maximum value |
| `step` | number | Increment step |
| `dualKnobs` | boolean | Two handles (returns `{lower, upper}`) |
| `snaps` | boolean | Snap to steps |
| `ticks` | boolean | Show tick marks |
| `pin` | boolean | Show value in pin above knob |

---

## ion-datetime

```html
<ion-item>
  <ion-label>Birthday</ion-label>
  <ion-datetime
    displayFormat="MMM D, YYYY"
    pickerFormat="MMMM D, YYYY"
    min="1990-01-01"
    max="2024-12-31"
    [(ngModel)]="birthDate">
  </ion-datetime>
</ion-item>

<!-- Time picker -->
<ion-datetime displayFormat="h:mm A" pickerFormat="h:mm A" [(ngModel)]="time">
</ion-datetime>
```

Format tokens: `YYYY` (year), `MM` (month 01-12), `MMM` (Jan-Dec), `MMMM` (January-December), `DD` (day 01-31), `D` (day 1-31), `HH` (24hr), `hh` (12hr), `mm` (minutes), `A` (AM/PM).

Values are stored as ISO 8601 strings, not JavaScript `Date` objects.

---

## ion-searchbar

```html
<ion-searchbar
  [(ngModel)]="searchQuery"
  (ionInput)="onSearch($event)"
  (ionCancel)="onCancel()"
  placeholder="Search..."
  showCancelButton="focus"
  animated>
</ion-searchbar>
```

| Attribute | Description |
|-----------|-------------|
| `showCancelButton` | `always`, `focus`, `never` |
| `animated` | Animate cancel button in/out |
| `debounce` | Debounce time in ms (default 250) |
| `(ionInput)` | Fires on each keystroke |
| `(ionChange)` | Fires when value is committed |
| `(ionCancel)` | Fires when cancel is tapped |
| `(ionClear)` | Fires when clear button is tapped |

---

## ion-segment / ion-segment-button

```html
<ion-segment [(ngModel)]="view" color="primary">
  <ion-segment-button value="friends">Friends</ion-segment-button>
  <ion-segment-button value="enemies">Enemies</ion-segment-button>
</ion-segment>

<!-- Conditional content -->
<div [ngSwitch]="view">
  <div *ngSwitchCase="'friends'">Friends list...</div>
  <div *ngSwitchCase="'enemies'">Enemies list...</div>
</div>
```

---

## ion-card

```html
<ion-card>
  <img src="assets/img/header.jpg"/>
  <ion-card-header>
    Card Header
  </ion-card-header>
  <ion-card-content>
    <ion-card-title>Card Title</ion-card-title>
    <p>Card body text...</p>
  </ion-card-content>
</ion-card>

<!-- Card with list -->
<ion-card>
  <ion-card-header>Recent Activity</ion-card-header>
  <ion-list>
    <ion-item *ngFor="let item of items">{{ item.title }}</ion-item>
  </ion-list>
</ion-card>
```

---

## ion-tabs / ion-tab

See [navigation.md](navigation.md) for the full Tabs API.

---

## ion-fab

Floating Action Button. Must be placed inside `<ion-content>`.

```html
<ion-content>
  <!-- FAB in corner -->
  <ion-fab bottom right>
    <button ion-fab color="primary">
      <ion-icon name="add"></ion-icon>
    </button>
  </ion-fab>

  <!-- FAB with speed dial -->
  <ion-fab bottom right>
    <button ion-fab>
      <ion-icon name="share"></ion-icon>
    </button>
    <ion-fab-list side="top">
      <button ion-fab (click)="shareTwitter()">
        <ion-icon name="logo-twitter"></ion-icon>
      </button>
      <button ion-fab (click)="shareFacebook()">
        <ion-icon name="logo-facebook"></ion-icon>
      </button>
    </ion-fab-list>
  </ion-fab>
</ion-content>
```

### FAB Position Attributes

Combine vertical and horizontal placement attributes on `<ion-fab>`:
- Vertical: `top`, `bottom`, `center`
- Horizontal: `left`, `right`, `center`
- `edge` — overlaps the header/footer edge

---

## ion-infinite-scroll

Loads more data when the user scrolls to the bottom.

```html
<ion-content>
  <ion-list>
    <ion-item *ngFor="let item of items">{{ item }}</ion-item>
  </ion-list>

  <ion-infinite-scroll (ionInfinite)="loadMore($event)" threshold="100px">
    <ion-infinite-scroll-content
      loadingSpinner="bubbles"
      loadingText="Loading more...">
    </ion-infinite-scroll-content>
  </ion-infinite-scroll>
</ion-content>
```

```typescript
loadMore(infiniteScroll: InfiniteScroll) {
  this.apiService.getNextPage().subscribe(newItems => {
    this.items.push(...newItems);
    infiniteScroll.complete();  // signal loading is done

    // Disable when no more data
    if (newItems.length === 0) {
      infiniteScroll.enable(false);
    }
  });
}
```

---

## ion-refresher

Pull-to-refresh on a list.

```html
<ion-content>
  <ion-refresher (ionRefresh)="doRefresh($event)">
    <ion-refresher-content
      pullingIcon="arrow-dropdown"
      pullingText="Pull to refresh"
      refreshingSpinner="circles"
      refreshingText="Refreshing...">
    </ion-refresher-content>
  </ion-refresher>

  <ion-list>...</ion-list>
</ion-content>
```

```typescript
doRefresh(refresher: Refresher) {
  this.apiService.getData().subscribe(data => {
    this.items = data;
    refresher.complete();  // stop the refresher animation
  });
}
```

---

## ion-virtual-scroll

Renders only visible items for performance with large lists.

```html
<ion-list [virtualScroll]="items" approxItemHeight="70px" [headerFn]="myHeaderFn">
  <ion-item-divider *virtualHeader="let header">
    {{ header }}
  </ion-item-divider>
  <ion-item *virtualItem="let item">
    <ion-label>
      <h2>{{ item.name }}</h2>
      <p>{{ item.detail }}</p>
    </ion-label>
  </ion-item>
</ion-list>
```

```typescript
myHeaderFn(record, recordIndex, records) {
  if (recordIndex === 0 || record.category !== records[recordIndex - 1].category) {
    return record.category;  // return header string
  }
  return null;  // no header
}
```

| Attribute | Description |
|-----------|-------------|
| `[virtualScroll]` | The data array |
| `approxItemHeight` | Estimated item height in px (e.g. `"70px"`) |
| `approxHeaderHeight` | Estimated header height |
| `approxFooterHeight` | Estimated footer height |
| `[headerFn]` | Function returning header label or null |
| `*virtualItem` | Structural directive for item template |
| `*virtualHeader` | Structural directive for header template |

---

## ion-slides / ion-slide

```html
<ion-slides [options]="slideOpts" (ionSlideDidChange)="slideChanged()">
  <ion-slide>
    <h1>Slide 1</h1>
    <p>Content for slide 1</p>
  </ion-slide>
  <ion-slide>
    <h1>Slide 2</h1>
  </ion-slide>
  <ion-slide>
    <h1>Slide 3</h1>
  </ion-slide>
</ion-slides>
```

```typescript
import { ViewChild } from '@angular/core';
import { Slides } from 'ionic-angular';

@Component({...})
export class MyPage {
  @ViewChild(Slides) slides: Slides;

  slideOpts = {
    loop: false,
    autoplay: 3000,      // ms between auto transitions
    speed: 400,          // transition speed in ms
    pager: true,         // show dots
    direction: 'horizontal',
    effect: 'slide',     // 'slide'|'fade'|'cube'|'coverflow'|'flip'
    initialSlide: 0,
    slidesPerView: 1,
    spaceBetween: 0
  };

  slideChanged() {
    console.log('Active index:', this.slides.getActiveIndex());
  }

  goToSlide(i: number) {
    this.slides.slideTo(i, 500);
  }

  next() { this.slides.slideNext(); }
  prev() { this.slides.slidePrev(); }
}
```

### Slides Methods

| Method | Description |
|--------|-------------|
| `slideTo(index, speed?)` | Navigate to specific slide |
| `slideNext(speed?)` | Next slide |
| `slidePrev(speed?)` | Previous slide |
| `getActiveIndex()` | Current slide index |
| `getPreviousIndex()` | Previous slide index |
| `length()` | Total slide count |
| `isBeginning()` | True if on first slide |
| `isEnd()` | True if on last slide |
| `lockSwipes(lock)` | Prevent swiping |
| `startAutoplay()` | Start auto-advance |
| `stopAutoplay()` | Stop auto-advance |

### Slides Events

`(ionSlideWillChange)`, `(ionSlideDidChange)`, `(ionSlideNextStart)`, `(ionSlidePrevStart)`, `(ionSlideReachStart)`, `(ionSlideReachEnd)`, `(ionSlideTap)`, `(ionSlideDoubleTap)`

---

## ion-item-sliding

Swipeable list items with reveal actions.

```html
<ion-list>
  <ion-item-sliding #slidingItem>
    <ion-item>
      <ion-label>Item Title</ion-label>
    </ion-item>

    <!-- Right swipe (default) -->
    <ion-item-options side="right">
      <button ion-button color="danger" (click)="delete(slidingItem)">
        <ion-icon name="trash" item-start></ion-icon>
        Delete
      </button>
      <button ion-button color="primary" (click)="archive(slidingItem)">
        Archive
      </button>
    </ion-item-options>

    <!-- Left swipe -->
    <ion-item-options side="left">
      <button ion-button color="secondary" expandable (click)="favorite(slidingItem)">
        <ion-icon name="star"></ion-icon>
        Favorite
      </button>
    </ion-item-options>
  </ion-item-sliding>
</ion-list>
```

`expandable` on a button makes it fill the full swipe area.

```typescript
delete(slidingItem: ItemSliding) {
  slidingItem.close();
  // perform delete
}
```

---

## ion-badge / ion-chip

```html
<!-- Badge on an item -->
<ion-item>
  <ion-label>Inbox</ion-label>
  <ion-badge item-end color="danger">5</ion-badge>
</ion-item>

<!-- Badge on a button -->
<button ion-button>
  Messages
  <ion-badge color="primary">3</ion-badge>
</button>

<!-- Chip -->
<ion-chip>
  <ion-avatar>
    <img src="assets/img/avatar.jpg">
  </ion-avatar>
  <ion-label>Alice</ion-label>
</ion-chip>

<ion-chip color="secondary" outline>
  <ion-icon name="pin"></ion-icon>
  <ion-label>San Francisco</ion-label>
</ion-chip>
```

---

## ion-note

Smaller text, typically for secondary information in items:

```html
<ion-item>
  <ion-label>
    <h2>Title</h2>
    <ion-note>Subtitle note text</ion-note>
  </ion-label>
  <ion-note item-end>Right note</ion-note>
</ion-item>
```

---

## ion-spinner

```html
<ion-spinner></ion-spinner>                    <!-- default platform spinner -->
<ion-spinner name="bubbles"></ion-spinner>
<ion-spinner name="circles"></ion-spinner>
<ion-spinner name="crescent"></ion-spinner>
<ion-spinner name="dots"></ion-spinner>
<ion-spinner name="lines"></ion-spinner>
<ion-spinner name="ios"></ion-spinner>
<ion-spinner color="primary"></ion-spinner>
```

---

## ion-reorder / ion-reorder-group

Allow users to drag and reorder list items.

```html
<ion-list>
  <ion-reorder-group (ionItemReorder)="reorderItems($event)">
    <ion-item *ngFor="let item of items">
      <ion-label>{{ item }}</ion-label>
      <ion-reorder item-end></ion-reorder>
    </ion-item>
  </ion-reorder-group>
</ion-list>
```

```typescript
reorderItems(indexes: { from: number, to: number }) {
  const element = this.items[indexes.from];
  this.items.splice(indexes.from, 1);
  this.items.splice(indexes.to, 0, element);
}
```

---

## ion-avatar / ion-thumbnail

```html
<!-- Avatar (circular) -->
<ion-avatar>
  <img src="assets/img/avatar.jpg">
</ion-avatar>

<!-- In an item -->
<ion-item>
  <ion-avatar item-start>
    <img src="assets/img/avatar.jpg">
  </ion-avatar>
  <ion-label>Alice</ion-label>
</ion-item>

<!-- Thumbnail (square) -->
<ion-thumbnail item-start>
  <img src="assets/img/thumb.jpg">
</ion-thumbnail>
```
