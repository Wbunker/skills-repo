# Ionic 4 — Data, HTTP & Storage

## Angular HttpClient

### Setup

```typescript
// app.module.ts
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [HttpClientModule, ...]
})
export class AppModule {}
```

### Service Pattern

```typescript
// services/api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getItems(): Observable<Item[]> {
    return this.http.get<Item[]>(`${this.baseUrl}/items`).pipe(
      catchError(this.handleError)
    );
  }

  getItem(id: number): Observable<Item> {
    return this.http.get<Item>(`${this.baseUrl}/items/${id}`);
  }

  createItem(item: Partial<Item>): Observable<Item> {
    return this.http.post<Item>(`${this.baseUrl}/items`, item);
  }

  updateItem(id: number, item: Partial<Item>): Observable<Item> {
    return this.http.put<Item>(`${this.baseUrl}/items/${id}`, item);
  }

  deleteItem(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/items/${id}`);
  }

  private handleError(error: any): Observable<never> {
    console.error('API error:', error);
    return throwError(error.message || 'Server error');
  }
}
```

### Using in a Page

```typescript
// home.page.ts
export class HomePage implements OnInit {
  items: Item[] = [];
  loading = false;
  error: string;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadItems();
  }

  ionViewWillEnter() {
    this.loadItems();  // refresh on return to page
  }

  loadItems() {
    this.loading = true;
    this.api.getItems().subscribe({
      next: (items) => {
        this.items = items;
        this.loading = false;
      },
      error: (err) => {
        this.error = err;
        this.loading = false;
      }
    });
  }
}
```

### HTTP Interceptors (Auth Token)

```typescript
// interceptors/auth.interceptor.ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler } from '@angular/common/http';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler) {
    const token = this.authService.getToken();
    if (token) {
      req = req.clone({
        setHeaders: { Authorization: `Bearer ${token}` }
      });
    }
    return next.handle(req);
  }
}

// Register in app.module.ts:
import { HTTP_INTERCEPTORS } from '@angular/common/http';
providers: [
  { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
]
```

---

## Ionic Storage

Ionic Storage is a key-value store that uses the best available storage engine (SQLite → IndexedDB → localStorage fallback).

### Install

```bash
npm install @ionic/storage-angular
# For SQLite backing (optional but recommended):
npm install cordova-sqlite-storage
ionic cordova plugin add cordova-sqlite-storage  # if using Cordova
```

### Setup (v3 API — used in Ionic v4)

```typescript
// app.module.ts
import { IonicStorageModule } from '@ionic/storage-angular';

@NgModule({
  imports: [
    IonicStorageModule.forRoot({
      name: '__mydb',
      driverOrder: ['sqlite', 'indexeddb', 'localstorage']
    })
  ]
})
export class AppModule {}
```

### Service Wrapper (Recommended Pattern)

Wrap Storage in a service to initialize it once and await readiness:

```typescript
// services/storage.service.ts
import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage-angular';

@Injectable({ providedIn: 'root' })
export class StorageService {
  private _storage: Storage | null = null;

  constructor(private storage: Storage) {
    this.init();
  }

  async init() {
    this._storage = await this.storage.create();
  }

  async set(key: string, value: any): Promise<any> {
    return this._storage?.set(key, value);
  }

  async get(key: string): Promise<any> {
    return this._storage?.get(key);
  }

  async remove(key: string): Promise<any> {
    return this._storage?.remove(key);
  }

  async clear(): Promise<void> {
    return this._storage?.clear();
  }

  async keys(): Promise<string[]> {
    return this._storage?.keys() ?? [];
  }
}
```

```typescript
// Usage in any component/service
constructor(private storageService: StorageService) {}

async save() {
  await this.storageService.set('user', { name: 'Alice', id: 1 });
}

async load() {
  const user = await this.storageService.get('user');
}
```

---

## Authentication Service Pattern

```typescript
// services/auth.service.ts
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { StorageService } from './storage.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private _isLoggedIn = new BehaviorSubject<boolean>(false);
  public isLoggedIn$ = this._isLoggedIn.asObservable();

  constructor(
    private storage: StorageService,
    private router: Router,
    private api: ApiService
  ) {
    this.checkToken();
  }

  async checkToken() {
    const token = await this.storage.get('auth_token');
    this._isLoggedIn.next(!!token);
  }

  async login(email: string, password: string): Promise<boolean> {
    try {
      const response: any = await this.api.post('/auth/login', { email, password }).toPromise();
      await this.storage.set('auth_token', response.token);
      this._isLoggedIn.next(true);
      return true;
    } catch {
      return false;
    }
  }

  async logout() {
    await this.storage.remove('auth_token');
    this._isLoggedIn.next(false);
    this.router.navigateByUrl('/login');
  }

  isLoggedIn(): boolean {
    return this._isLoggedIn.value;
  }

  async getToken(): Promise<string | null> {
    return this.storage.get('auth_token');
  }
}
```

---

## RxJS Patterns in Ionic Services

```typescript
import { BehaviorSubject, Observable, from } from 'rxjs';
import { switchMap, tap, map } from 'rxjs/operators';

// BehaviorSubject for state that pages can subscribe to
private items$ = new BehaviorSubject<Item[]>([]);

// Convert Promise to Observable
getFromStorage(): Observable<Item[]> {
  return from(this.storage.get('items')).pipe(
    map(data => data || [])
  );
}

// Refresh pattern
refresh(): Observable<Item[]> {
  return this.api.getItems().pipe(
    tap(items => this.items$.next(items))
  );
}
```

---

## Loading State Pattern (with IonLoading)

```typescript
async loadWithSpinner<T>(promise: Promise<T>, message = 'Loading...'): Promise<T> {
  const loading = await this.loadingCtrl.create({ message });
  await loading.present();
  try {
    return await promise;
  } finally {
    await loading.dismiss();
  }
}

// Usage:
const items = await this.loadWithSpinner(
  this.api.getItems().toPromise(),
  'Fetching items...'
);
```

---

## Environment Variables

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'https://dev-api.example.com',
  googleMapsKey: 'YOUR_DEV_KEY'
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://api.example.com',
  googleMapsKey: 'YOUR_PROD_KEY'
};

// Use in a service:
import { environment } from '../../environments/environment';
const url = environment.apiUrl;
```
