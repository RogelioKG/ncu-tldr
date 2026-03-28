# 🎓 NCU-TLDR (中大課程評價平台)

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![Vue3](https://img.shields.io/badge/Frontend-Vue3-4fc08d?style=flat&logo=vue.js)
![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=flat&logo=vite)
![Python](https://img.shields.io/badge/Backend-Python-3776AB?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-005571?style=flat&logo=fastapi)

## 🌟 核心理念

本專案旨在解決選課時「評價散亂」與「資訊不對稱」的痛點。我們相信評價應該是**匿名、真實且具建設性**的。

- **🔒 絕對匿名**：對外完全隱藏身分，僅限校內學生驗證存取。
- **🤖 AI 摘要**：利用大語言模型將數百則評論濃縮成精簡的課程懶人包。
- **⚖️ 權重機制**：引入動態可信度演算法，優質評論自動獲得更高影響力。
- **⚡ 極簡填寫**：隨意輸入心得，AI 自動幫你分類標籤與結構化。

---

## ✨ 重點功能

- **AI 課程小卡**：主頁快速顯示星等、甜涼度與 AI 自動生成的 `#Hashtag`。
- **可信度加權系統**：星等計算並非簡單平均，而是根據使用者過往貢獻度進行加權。
- **倖存者偏差提示**：透明顯示評價覆蓋率，讓使用者知道資訊的代表性。
- **身分牆**：整合學校信箱驗證，確保只有真正的在校生能參與討論。

## 🛠️ 技術架構

本專案採用 **Monorepo** 架構進行管理，前後端分離設計。

| 領域 | 技術選型 | 說明 |
| :--- | :--- | :--- |
| **Frontend** | Vue 3 (Composition API) | 使用 setup 語法糖，配合 TypeScript 開發 |
| **Build Tool** | Vite | 極速的開發伺服器與建置工具 |
| **Styling** | CSS Variables | 原生 CSS 變數實現響應式與主題管理 |
| **Backend** | Python (FastAPI) | *開發中* - 高性能異步 Web 框架 |
| **Database** | PostgreSQL | *規劃中* - 關聯式資料庫 |
| **Testing** | Vitest | 單元測試與元件測試 |

## 📂 目錄架構

```text
NCU-TLDR/
├── backend/                  # 後端應用程式 (Python/FastAPI)
│   ├── main.py               # 應用程式入口
│   └── requirements.txt      # Python 依賴清單
├── frontend/                 # 前端應用程式 (Vue 3 + Vite)
│   ├── public/               # 公共靜態資源
│   ├── src/                  # 原始碼目錄
│   │   ├── components/       # Vue 共用元件 (CourseCard, NavBar...)
│   │   ├── views/            # 頁面視圖 (HomeView, CourseDetailView)
│   │   ├── router/           # 路由設定
│   │   ├── types/            # TypeScript 型別定義
│   │   ├── mock/             # 開發用模擬資料
│   │   ├── assets/           # 靜態資源 (圖片、圖示)
│   │   └── style.css         # 全域樣式定義
│   ├── index.html            # 應用程式入口點
│   └── vite.config.ts        # Vite 設定檔
├── docs/                     # 專案文件
│   └── database-design.md    # 資料庫設計文件
├── docker-compose.yml        # Docker 開發環境（db + backend + frontend）
├── docker-compose.dev.yml    # 選用：前端 hot reload 進階設定
├── docker-compose.prod.yml   # 生產環境覆寫（日後使用）
├── .dockerignore             # Docker build context 忽略規則
├── pnpm-workspace.yaml       # Monorepo Workspace 設定
└── README.md                 # 專案說明文件
```

## 🚀 快速上手

### 環境需求

- **docker compose**: v2.22.0+ (支援 `watch` 功能)
- **node**: v20+
- **python**: v3.12+
- **pnpm**: v9+
- **uv**: v0.9+

### 安裝步驟

本專案已配置好完整的 Docker 環境，並支援熱重載 (Hot Reload)，建議直接透過 Docker 進行開發。

1. **Clone 專案**
   ```bash
   git clone https://github.com/RogelioKG/ncu-tldr.git
   cd ncu-tldr
   ```

2. **啟動開發環境**
   ```bash
   pnpm run docker:dev:watch
   ```

3. **資料庫初始化**
   ```
   docker exec -it ncu-tldr-dev-backend alembic upgrade head
   ```

4. **資料庫灌入資料**
   ```bash
   cd ./backend/scripts
   curl -X POST http://localhost:8000/api/admin/sync -H "X-SYNC-SECRET-KEY: change-me-in-production" -H "Content-Type: application/json" -d "@all.json"
   ```

5. **開始開發**
   - 前端：[http://localhost:5173](http://localhost:5173)
   - 後端 API 文檔：[http://localhost:8000/docs](http://localhost:8000/docs)

## 🐳 Docker

本專案採用 **Multi-stage Build** 與 **Compose Watch**。

### 開發環境 (dev)
+ 啟動 (熱重載)
   ```bash
   pnpm run docker:dev:watch
   ```
+ 關閉 (移除容器)
   ```bash
   pnpm run docker:dev:down
   ```

### 正式環境 (prod)
+ 啟動
   ```bash
   pnpm run docker:prod:up
   ```
+ 關閉 (移除容器)
   ```bash
   pnpm run docker:prod:down
   ```

## 🤝 參與貢獻

我們非常歡迎任何形式的貢獻！無論是回報 Bug、提出新功能建議，或是直接提交 PR。

1. Fork 本專案
2. 建立您的 Feature Branch (`git checkout -b feature/AmazingFeature`)
3. 提交您的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 [AGPL-3.0 License](LICENSE) 授權。
