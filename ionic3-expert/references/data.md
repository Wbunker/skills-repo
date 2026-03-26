# Ionic 3 — Data & Services

## Angular HttpClient

Ionic 3 ships with Angular 4–6. Use `HttpClientModule` (Angular 4.3+) rather than the deprecated `HttpModule`.

### Setup in app.module.ts

```typescript
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [
    BrowserModule,
    HttpClientModule,    // add here
    IonicModule.forRoot(MyApp)
  ]
})
export class AppModule {}
```

### Creating an API Service

```typescript
// src/providers/api/api.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/observable/throw';

@Injectable()
export class ApiService {
  private baseUrl = 'https://api.example.com';

  constructor(private http: HttpClient) {}

  getItems(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/items`);
  }

  getItem(id: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/items/${id}`);
  }

  createItem(item: any): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post<any>(`${this.baseUrl}/items`, item, { headers });
  }

  updateItem(id: number, item: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/items/${id}`, item);
  }

  deleteItem(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/items/${id}`);
  }

  searchItems(query: string): Observable<any[]> {
    const params = new HttpParams().set('q', query).set('limit', '20');
    return this.http.get<any[]>(`${this.baseUrl}/search`, { params });
  }
}
```

### Register Provider

```typescript
// app.module.ts providers:
providers: [
  ApiService,
  // ... other providers
]
```

Or use `@Injectable()` with `providedIn: 'root'` in Angular 6+ (available in late Ionic 3 projects with Angular 6).

---

## RxJS in Ionic 3

Ionic 3 projects use **RxJS 5.x** (not RxJS 6). The import paths and usage patterns differ from modern RxJS.

### RxJS 5 Import Style

```typescript
// Import Observable
import { Observable } from 'rxjs/Observable';

// Import specific operators (patch method style)
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/distinctUntilChanged';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/operator/mergeMap';
import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/tap';
import 'rxjs/add/operator/finally';

// Import Observable static creators
import 'rxjs/add/observable/of';
import 'rxjs/add/observable/from';
import 'rxjs/add/observable/throw';
import 'rxjs/add/observable/forkJoin';
import 'rxjs/add/observable/interval';
import 'rxjs/add/observable/timer';

// Subject
import { Subject } from 'rxjs/Subject';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { ReplaySubject } from 'rxjs/ReplaySubject';
```

### Common RxJS 5 Patterns

```typescript
// Map + subscribe
this.http.get<Item[]>('/api/items')
  .map(items => items.filter(i => i.active))
  .subscribe(items => {
    this.items = items;
  }, err => {
    console.error(err);
  });

// Error handling with catch
this.http.get('/api/data')
  .catch(error => Observable.throw(error.message || 'Server error'))
  .subscribe(data => { ... }, err => { ... });

// chaining operators
this.searchSubject
  .debounceTime(300)
  .distinctUntilChanged()
  .switchMap(query => this.api.search(query))
  .subscribe(results => {
    this.results = results;
  });

// BehaviorSubject as a state store
private userSubject = new BehaviorSubject<User>(null);
user$ = this.userSubject.asObservable();

setUser(user: User) {
  this.userSubject.next(user);
}

getUser(): User {
  return this.userSubject.getValue();
}

// forkJoin — parallel requests
Observable.forkJoin([
  this.api.getUser(id),
  this.api.getPosts(id)
]).subscribe(([user, posts]) => {
  this.user = user;
  this.posts = posts;
});

// Converting Promise to Observable
import 'rxjs/add/observable/fromPromise';
Observable.fromPromise(this.storage.get('user'))
  .subscribe(user => console.log(user));
```

### RxJS 5 vs RxJS 6 Comparison

| RxJS 5 (Ionic 3) | RxJS 6 (Ionic 4+) |
|-------------------|-------------------|
| `import { Observable } from 'rxjs/Observable'` | `import { Observable } from 'rxjs'` |
| `.map(fn)` (method chaining) | `.pipe(map(fn))` |
| `import 'rxjs/add/operator/map'` | `import { map } from 'rxjs/operators'` |
| `Observable.of(x)` | `of(x)` |
| `Observable.forkJoin([...])` | `forkJoin([...])` |
| `Observable.fromPromise(p)` | `from(p)` |
| `Observable.throw(err)` | `throwError(err)` |

---

## Provider Pattern (Angular Services)

In Ionic 3, services are called "providers". Generated via:

```bash
ionic generate provider providers/auth
```

```typescript
// src/providers/auth/auth.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { Storage } from '@ionic/storage';

@Injectable()
export class AuthProvider {
  private apiUrl = 'https://api.example.com';

  constructor(
    private http: HttpClient,
    private storage: Storage
  ) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, { email, password })
      .map((res: any) => {
        this.storage.set('token', res.token);
        return res;
      });
  }

  logout(): Promise<void> {
    return this.storage.remove('token');
  }

  isAuthenticated(): Promise<boolean> {
    return this.storage.get('token').then(token => !!token);
  }

  getToken(): Promise<string> {
    return this.storage.get('token');
  }
}
```

### Registering Providers

Add to `providers` array in `app.module.ts`:

```typescript
providers: [
  AuthProvider,
  ApiService,
  StatusBar,
  SplashScreen,
  { provide: ErrorHandler, useClass: IonicErrorHandler }
]
```

For lazy-loaded modules, providers declared in child module are local to that module. To share a single instance app-wide, only declare in `app.module.ts`.

---

## HTTP Interceptors

```typescript
// src/providers/auth-interceptor/auth-interceptor.ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/fromPromise';
import 'rxjs/add/operator/mergeMap';

import { Storage } from '@ionic/storage';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private storage: Storage) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return Observable.fromPromise(this.storage.get('token'))
      .mergeMap(token => {
        if (token) {
          request = request.clone({
            setHeaders: { Authorization: `Bearer ${token}` }
          });
        }
        return next.handle(request);
      });
  }
}
```

Register in `app.module.ts`:

```typescript
import { HTTP_INTERCEPTORS } from '@angular/common/http';

providers: [
  {
    provide: HTTP_INTERCEPTORS,
    useClass: AuthInterceptor,
    multi: true
  }
]
```

---

## Ionic Storage (@ionic/storage v2)

See also [native.md](native.md) for installation.

```typescript
import { Storage } from '@ionic/storage';

@Injectable()
export class DataService {
  constructor(private storage: Storage) {}

  // All methods return Promises
  save(key: string, value: any): Promise<any> {
    return this.storage.set(key, value);
  }

  load(key: string): Promise<any> {
    return this.storage.get(key);
  }

  delete(key: string): Promise<any> {
    return this.storage.remove(key);
  }

  wipe(): Promise<void> {
    return this.storage.clear();
  }

  // Iterate all entries
  listAll() {
    return this.storage.forEach((value, key, index) => {
      console.log(key, value);
    });
  }

  // Total number of keys
  count(): Promise<number> {
    return this.storage.length();
  }
}
```

### IonicStorageModule Configuration

```typescript
IonicStorageModule.forRoot({
  name: '__myapp',
  driverOrder: ['sqlite', 'indexeddb', 'websql', 'localstorage']
})
```

Driver priority (first available is used):
1. `sqlite` — native SQLite via Cordova plugin (device only)
2. `indexeddb` — browser/web
3. `websql` — browser (legacy)
4. `localstorage` — fallback

---

## Environment Files

Ionic 3 does not have built-in Angular CLI environment file support (like `environment.prod.ts`). Common approaches:

### Manual Environment Files

```typescript
// src/app/config.ts
const PROD = false;

export const ENV = {
  production: PROD,
  apiUrl: PROD
    ? 'https://api.myapp.com'
    : 'http://localhost:3000',
  wsUrl: PROD
    ? 'wss://api.myapp.com'
    : 'ws://localhost:3000',
  appName: 'My App'
};
```

Import in services:

```typescript
import { ENV } from '../../app/config';

private baseUrl = ENV.apiUrl;
```

### webpack Environment Replacement (Advanced)

Some teams use `ionic-app-scripts` custom webpack config to swap config files at build time:

```json
// package.json scripts
"build:prod": "ionic-app-scripts build --prod --env prod"
```

```javascript
// webpack.config.js (custom)
const ENV = process.env.IONIC_ENV;
module.exports = {
  resolve: {
    alias: {
      '@app/env': path.resolve(environmentPath)
    }
  }
};
```

---

## HTTP (Legacy — Angular 2/4)

The old `Http` module (deprecated in Angular 4.3, removed later):

```typescript
// LEGACY — use HttpClient instead
import { Http, Headers, RequestOptions } from '@angular/http';
import 'rxjs/add/operator/map';

this.http.get('/api/items')
  .map(res => res.json())   // manual JSON parsing — not needed with HttpClient
  .subscribe(data => { ... });
```

`HttpClient` (from `@angular/common/http`) automatically parses JSON and provides typed responses. Always prefer `HttpClient` for new Ionic 3 code.

---

## State Management Patterns

### BehaviorSubject Service Store

Simple shared state without additional libraries:

```typescript
// src/providers/state/state.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';

@Injectable()
export class StateService {
  private _currentUser = new BehaviorSubject<User>(null);
  private _cartItems = new BehaviorSubject<CartItem[]>([]);

  currentUser$ = this._currentUser.asObservable();
  cartItems$ = this._cartItems.asObservable();

  setUser(user: User) { this._currentUser.next(user); }
  getUser(): User { return this._currentUser.getValue(); }

  addToCart(item: CartItem) {
    const current = this._cartItems.getValue();
    this._cartItems.next([...current, item]);
  }
}
```

Subscribe in components:

```typescript
constructor(private state: StateService) {}

ionViewWillEnter() {
  this.state.currentUser$.subscribe(user => {
    this.user = user;
  });
}
```

### Ionic Events (Pub/Sub)

Built-in event bus for component communication:

```typescript
import { Events } from 'ionic-angular';

// Publisher
this.events.publish('user:login', { userId: 123, time: new Date() });

// Subscriber
this.events.subscribe('user:login', (data) => {
  console.log('User logged in:', data.userId);
});

// Unsubscribe
this.events.unsubscribe('user:login');
```

Use Events for cross-page communication; prefer Observables/BehaviorSubject for services sharing state.
