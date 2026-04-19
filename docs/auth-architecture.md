# NCU-TLDR 全站驗證架構

> 實作分支：`feature/fundamentals`
> 最後更新：2026-04-19

---

## 目錄

1. [概覽](#概覽)
2. [元件架構](#元件架構)
3. [Token 設計](#token-設計)
4. [資料庫結構](#資料庫結構)
5. [完整流程圖](#完整流程圖)
   - [應用程式啟動與 Hydration](#應用程式啟動與-hydration)
   - [註冊與 Email 驗證](#註冊與-email-驗證)
   - [登入](#登入)
   - [已認證的 API 請求](#已認證的-api-請求)
   - [無聲刷新（Silent Refresh）](#無聲刷新silent-refresh)
   - [Refresh Token 輪換](#refresh-token-輪換)
   - [Token 盜用偵測](#token-盜用偵測)
   - [登出](#登出)
   - [路由守衛](#路由守衛)
6. [安全設計決策](#安全設計決策)
7. [設定參數](#設定參數)

---

## 概覽

NCU-TLDR 使用 **JWT Access Token + Rotating Refresh Token** 的雙 Token 架構，透過 **HttpOnly Cookie** 傳輸，完全不依賴 `localStorage`。

| 特性 | 說明 |
|------|------|
| Access Token | JWT，有效期 15 分鐘，儲存於 `HttpOnly Cookie` |
| Refresh Token | 隨機字串，有效期 1 天（記住我：30 天），SHA-256 hash 儲存於 DB |
| 傳輸機制 | Browser 自動帶入 Cookie（`credentials: 'include'`） |
| JS 存取 | 無法存取（HttpOnly），防止 XSS 竊取 |
| CSRF 防護 | `SameSite=Lax`，跨站請求不自動帶入 |
| 輪換策略 | 每次使用 Refresh Token 即廢止舊 Token、發行新 Token |
| 盜用偵測 | 重複使用已廢止 Token → 廢止該 User 所有 Token |

---

## 元件架構

```mermaid
graph TB
    subgraph Frontend["前端 (Vue 3)"]
        direction TB
        MT["main.ts<br/>啟動時 hydrate"]
        RG["Router Guard<br/>beforeEach()"]
        Store["useAuthStore (Pinia)<br/>user / isLoggedIn"]
        AuthAPI["api/auth.ts<br/>login / getMe / logoutApi"]
        Client["api/client.ts<br/>request() + 自動 silent refresh"]
    end

    subgraph Backend["後端 (FastAPI)"]
        direction TB
        EP["Auth Endpoints<br/>/login /refresh /logout /me"]
        DEP["get_current_user dep<br/>Cookie → JWT decode → DB lookup"]
        SVC["AuthService<br/>_issue_tokens / refresh / logout"]
        SEC["core/security.py<br/>JWT encode/decode<br/>hash_token / generate_refresh_token_str"]
        REPO["RefreshTokenRepository<br/>create / get_by_hash / revoke / revoke_all"]
    end

    subgraph DB["PostgreSQL"]
        UT["users"]
        RT["refresh_tokens<br/>token_hash / expires_at / revoked_at"]
        EVT["email_verification_tokens"]
    end

    Browser["瀏覽器 Cookie Jar<br/>access_token (path=/)<br/>refresh_token (path=/api/v1/auth)"]

    MT --> Store
    Store --> AuthAPI
    AuthAPI --> Client
    Client -- "credentials: include" --> EP
    RG --> Store

    EP --> DEP
    EP --> SVC
    DEP --> SEC
    SVC --> SEC
    SVC --> REPO
    REPO --> RT
    DEP --> UT
    SVC --> UT
    SVC --> EVT

    EP -- "Set-Cookie" --> Browser
    Browser -- "自動帶入 Cookie" --> Client
```

---

## Token 設計

```mermaid
graph LR
    subgraph AT["Access Token (JWT)"]
        AT1["Header: alg=HS256"]
        AT2["Payload: sub=user_id, exp=now+15min"]
        AT3["Signature: HMAC-SHA256(secret)"]
    end

    subgraph RT["Refresh Token"]
        RT1["原始值: secrets.token_urlsafe(48)<br/>~64 個 URL-safe 字元"]
        RT2["DB 儲存: SHA-256(raw)<br/>64 hex chars"]
        RT3["Cookie 值: 原始值<br/>瀏覽器無法讀取（HttpOnly）"]
    end

    subgraph Cookies["Cookie 設定"]
        C1["access_token<br/>path=/<br/>max_age=900s<br/>HttpOnly, SameSite=Lax"]
        C2["refresh_token<br/>path=/api/v1/auth<br/>max_age=86400s 或 2592000s<br/>HttpOnly, SameSite=Lax"]
    end

    AT --> C1
    RT1 --> RT3
    RT1 --> RT2
    RT3 --> C2
```

**重要設計：** Refresh Token Cookie 的 `path=/api/v1/auth` 確保瀏覽器只在呼叫 `/api/v1/auth/*` 端點時才帶入，降低 Token 洩漏範圍。

---

## 資料庫結構

```mermaid
erDiagram
    users {
        uuid id PK
        string email UK
        string hashed_password
        string display_name
        boolean is_active
        boolean email_verified
        timestamp created_at
    }

    refresh_tokens {
        uuid id PK
        uuid user_id FK
        string token_hash UK "SHA-256, 64 chars"
        timestamp expires_at
        timestamp revoked_at "NULL = 有效"
        timestamp created_at
    }

    email_verification_tokens {
        uuid id PK
        uuid user_id FK
        string token UK
        timestamp expires_at
        timestamp used_at "NULL = 未使用"
    }

    users ||--o{ refresh_tokens : "has"
    users ||--o{ email_verification_tokens : "has"
```

---

## 完整流程圖

### 應用程式啟動與 Hydration

```mermaid
sequenceDiagram
    participant B as 瀏覽器
    participant M as main.ts
    participant S as useAuthStore
    participant API as GET /api/v1/auth/me
    participant R as Vue Router

    B->>M: 載入頁面
    M->>S: auth.hydrateFromStorage()
    S->>API: GET /me (帶入 access_token cookie)
    alt Cookie 有效
        API-->>S: 200 UserOut
        S->>S: user.value = UserOut
    else Cookie 不存在或過期
        API-->>S: 401
        S->>S: user.value = null
    end
    M->>M: .finally() → app.mount('#app')
    Note over M,R: 無論成功或失敗，App 都會掛載
    B->>R: 導向目標路由
```

> `finally()` 確保即使 `getMe()` 失敗（使用者未登入），App 也一定掛載，不會白屏。

---

### 註冊與 Email 驗證

```mermaid
sequenceDiagram
    participant U as 使用者
    participant FE as 前端
    participant BE as POST /register
    participant Mail as AWS SES
    participant VE as GET /verify-email?token=...
    participant DB as PostgreSQL

    U->>FE: 填寫 email / password / 名稱
    FE->>BE: POST /api/v1/auth/register
    BE->>DB: 建立 user (email_verified=false)
    BE->>DB: 建立 email_verification_token
    BE->>Mail: 寄送驗證信
    Mail-->>U: 驗證信 (含 token 連結)
    BE-->>FE: 200 { message: "驗證信已寄出..." }

    U->>VE: 點擊驗證連結
    VE->>DB: 查詢 token，驗證未使用且未過期
    VE->>DB: 標記 token 為已使用
    VE->>DB: 更新 user.email_verified = true
    VE->>DB: 建立 refresh_token (hash)
    VE-->>U: Set-Cookie: access_token + refresh_token
    VE-->>U: 200 UserOut，自動登入
```

---

### 登入

```mermaid
sequenceDiagram
    participant U as 使用者
    participant FE as 前端
    participant BE as POST /login
    participant DB as PostgreSQL

    U->>FE: email / password / remember_me
    FE->>BE: POST /api/v1/auth/login
    BE->>DB: 查詢 user by email
    BE->>BE: bcrypt 驗證密碼
    alt 密碼正確且 email 已驗證
        BE->>BE: create_access_token(user_id) → JWT
        BE->>BE: generate_refresh_token_str() → raw
        BE->>BE: hash_token(raw) → SHA-256
        BE->>DB: INSERT refresh_tokens(token_hash, expires_at)
        BE-->>FE: Set-Cookie: access_token (15min)<br/>Set-Cookie: refresh_token (1d 或 30d)
        BE-->>FE: 200 UserOut
        FE->>FE: useAuthStore.user = UserOut
    else 密碼錯誤或 email 未驗證
        BE-->>FE: 401 / 403
    end
```

---

### 已認證的 API 請求

```mermaid
sequenceDiagram
    participant FE as 前端元件
    participant Client as api/client.ts
    participant BE as 受保護端點
    participant DEP as get_current_user dep
    participant DB as PostgreSQL

    FE->>Client: request('/api/v1/some-endpoint')
    Client->>BE: fetch (自動帶入 access_token cookie)
    BE->>DEP: Cookie('access_token')
    DEP->>DEP: decode_access_token() → user_id (JWT 驗簽 + exp)
    DEP->>DB: user_repo.get_by_id(user_id)
    DB-->>DEP: User
    DEP-->>BE: User 物件
    BE-->>Client: 200 + 資料
    Client-->>FE: 解析後的資料
```

---

### 無聲刷新（Silent Refresh）

當 Access Token 過期，前端自動刷新，使用者無感。

```mermaid
sequenceDiagram
    participant FE as 前端元件
    participant Client as api/client.ts
    participant API as 受保護端點
    participant Refresh as POST /refresh
    participant BE as AuthService.refresh()

    FE->>Client: request('/api/v1/some-endpoint')
    Client->>API: fetch (帶過期的 access_token)
    API-->>Client: 401 Unauthorized

    Note over Client: _isRetry=false, path≠/refresh → 嘗試刷新
    Client->>Refresh: POST /api/v1/auth/refresh (帶 refresh_token cookie)
    Refresh->>BE: 驗證 refresh_token
    BE-->>Refresh: 200 + 新 Token
    Refresh-->>Client: Set-Cookie: 新的 access_token + refresh_token
    Note over Client: _isRetry=true，不再觸發刷新
    Client->>API: 重試原始請求（帶新 access_token）
    API-->>Client: 200 + 資料
    Client-->>FE: 解析後的資料
```

---

### Refresh Token 輪換

每次使用 Refresh Token 都會廢止舊 Token、發行新 Token。

```mermaid
sequenceDiagram
    participant FE as 前端
    participant BE as POST /refresh
    participant SVC as AuthService
    participant DB as PostgreSQL

    FE->>BE: POST /refresh (refresh_token cookie = raw_R1)
    BE->>SVC: refresh(db, raw_R1)
    SVC->>SVC: hash_token(raw_R1) → H1
    SVC->>DB: SELECT * FROM refresh_tokens WHERE token_hash=H1

    alt Token 有效（revoked_at IS NULL, expires_at 未過期）
        DB-->>SVC: RefreshToken record
        SVC->>DB: UPDATE revoked_at=now() WHERE token_hash=H1
        SVC->>SVC: generate_refresh_token_str() → raw_R2
        SVC->>SVC: hash_token(raw_R2) → H2
        SVC->>DB: INSERT refresh_tokens(token_hash=H2, ...)
        SVC->>SVC: create_access_token() → new JWT
        BE-->>FE: Set-Cookie: 新 access_token + refresh_token=R2
    else Token 已廢止（revoked_at IS NOT NULL）
        Note over SVC: 偵測到重複使用，可能是 Token 盜用
        SVC->>DB: UPDATE revoked_at=now() WHERE user_id=... AND revoked_at IS NULL
        BE-->>FE: 401 "Refresh token reuse detected"
    else Token 過期
        BE-->>FE: 401 "Refresh token expired"
    end
```

---

### Token 盜用偵測

若攻擊者取得並先使用了 Refresh Token，合法使用者的重試會觸發盜用偵測。

```mermaid
sequenceDiagram
    participant Attacker as 攻擊者
    participant Victim as 合法使用者
    participant BE as POST /refresh
    participant DB as PostgreSQL

    Note over Attacker,Victim: 攻擊者取得 raw_R1（例如網路攔截）

    Attacker->>BE: POST /refresh (R1) ← 搶先使用
    BE->>DB: R1 hash 查到，revoked_at=NULL → 有效
    BE->>DB: 廢止 R1，發行 R2
    BE-->>Attacker: 成功，取得新 Cookie (R2)

    Victim->>BE: POST /refresh (R1) ← 舊 Token
    BE->>DB: R1 hash 查到，revoked_at IS NOT NULL ← 已被廢止！
    Note over BE: 偵測到 Token 重用 → 核彈選項
    BE->>DB: UPDATE refresh_tokens SET revoked_at=now()<br/>WHERE user_id=X AND revoked_at IS NULL
    Note over DB: 廢止 R2 及所有其他有效 Token
    BE-->>Victim: 401 "Refresh token reuse detected"
    BE-->>Attacker: 下次 R2 也被廢止，401
    Note over Victim: 使用者被強制重新登入
```

---

### 登出

```mermaid
sequenceDiagram
    participant U as 使用者
    participant FE as 前端
    participant BE as POST /logout
    participant DB as PostgreSQL

    U->>FE: 點擊登出
    FE->>BE: POST /api/v1/auth/logout (帶 refresh_token cookie)
    BE->>BE: hash_token(raw_refresh) → hash
    BE->>DB: SELECT refresh_token WHERE token_hash=hash
    BE->>DB: UPDATE revoked_at=now() (若尚未廢止)
    BE-->>FE: Set-Cookie: access_token='' max_age=0<br/>Set-Cookie: refresh_token='' max_age=0
    BE-->>FE: 200 { message: "已登出" }
    FE->>FE: useAuthStore.user = null
    FE->>FE: 導向登入頁
```

---

### 路由守衛

```mermaid
flowchart TD
    NAV["使用者導向某路由"] --> CHECK{to.meta.requiresAuth?}
    CHECK -- No --> ALLOW["直接放行"]
    CHECK -- Yes --> STORE["動態 import useAuthStore"]
    STORE --> LOGIN_CHECK{auth.isLoggedIn?}
    LOGIN_CHECK -- Yes --> ALLOW
    LOGIN_CHECK -- No --> REDIRECT["導向 /login?redirect=原路徑"]

    subgraph Note["注意"]
        N1["動態 import 避免循環依賴<br/>（router ↔ store）"]
        N2["hydration 在 main.ts 完成後<br/>才掛載 App，guard 執行時<br/>isLoggedIn 已是正確狀態"]
    end
```

**需要登入的路由（`meta: { requiresAuth: true }`）：**

| 路由 | 路徑 |
|------|------|
| 首頁 | `/` |
| 課程詳情 | `/course/:id` |
| 我的評論 | `/my-reviews` |
| 我的等級 | `/my-level` |

---

## 安全設計決策

### HttpOnly Cookie vs localStorage

| | HttpOnly Cookie | localStorage |
|---|---|---|
| XSS 竊取 | **不可能**（JS 無法讀取） | 可直接讀取 |
| CSRF | 需 SameSite 設定 | 無 CSRF 風險 |
| 跨分頁同步 | 自動 | 需手動同步 |

### SameSite=Lax

跨站的 POST/PUT/DELETE 請求不會自動帶入 Cookie，防止 CSRF 攻擊。GET 請求（點擊連結導航）允許帶入，不影響 email 驗證連結的使用。

### Refresh Token 的 Cookie Path 限制

```
access_token   → path=/               所有 API 請求都能用
refresh_token  → path=/api/v1/auth    只有 /api/v1/auth/* 才帶入
```

Refresh Token 不會在普通 API 請求中洩漏，只在真正需要刷新時才被傳輸。

### 無聲刷新（Silent Refresh）的防無限迴圈設計

```typescript
// _isRetry=true 表示已重試過，不再觸發刷新
// path !== '/api/v1/auth/refresh' 防止刷新請求本身失敗時無窮遞迴
if (response.status === 401 && !_isRetry && path !== '/api/v1/auth/refresh') {
    // 嘗試刷新...
    return request<T>(path, options, true)  // _isRetry=true
}
```

### DB 儲存 Hash 而非原始 Token

資料庫只儲存 SHA-256(raw_token)。即使 DB 被盜，攻擊者也無法直接使用 hash 登入（hash 無法反推原始 Token）。

---

## 設定參數

| 環境變數 | 預設值 | 說明 |
|---------|--------|------|
| `JWT_SECRET_KEY` | (必填) | JWT 簽名密鑰 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access Token 有效期（分鐘） |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `1` | Refresh Token 有效期（天） |
| `REFRESH_TOKEN_REMEMBER_ME_EXPIRE_DAYS` | `30` | 記住我模式有效期（天） |
| `COOKIE_SECURE` | `true` | 生產環境應為 `true`（HTTPS only）；本機開發設為 `false` |
| `COOKIE_SAMESITE` | `lax` | Cookie SameSite 屬性 |

**本機開發 `.env` 建議設定：**

```env
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```
