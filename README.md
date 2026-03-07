# 🎓 NCU-TLDR (中大課程評價平台)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
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

- **Node.js**: v20+
- **pnpm**: v9+
- **Python**: v3.12+ (後端開發用)
- **Docker Desktop**: 最新穩定版 (含 `docker compose`)

### 安裝步驟

1. **Clone 專案**
   ```bash
   git clone https://github.com/your-username/NCU-TLDR.git
   cd NCU-TLDR
   ```

2. **安裝依賴 (Frontend)**
   ```bash
   cd frontend
   pnpm install
   ```

3. **啟動開發伺服器**
   ```bash
   pnpm run dev
   ```
   瀏覽器將自動開啟 `http://localhost:5173`。

## 🐳 Docker 開發（後端建置）

目前以**單一開發流程**為主，不區分 dev/prod compose。後端為單一 stage 建置，volume mount 支援 hot reload。

### 後端建置與啟動

一鍵啟動 DB + Backend + Frontend（皆含 volume、hot reload）：

```bash
docker compose up --build
```

- **Frontend**: http://localhost:5173  
- **Backend**: http://localhost:8000  
- **PostgreSQL**: localhost:5432  

後端目錄 `./backend` 已掛載進容器，改碼後 uvicorn `--reload` 會自動重啟。

### 本機僅跑後端（不用 Docker）

若只在本機開發後端、DB 用 Docker：

```bash
# 終端 1：只起 DB
docker compose up db -d

# 終端 2：backend 目錄用 uv
cd backend
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

需設定 `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ncu_tldr`（或 `.env`）。

### Alembic Migration

```bash
docker compose exec backend uv run alembic upgrade head
```

### 注意事項

- 容器內連 DB 請用 service name `db`，勿用 `localhost`。
- 資料庫資料持久化於 volume `pgdata`。
- 生產用 `docker-compose.prod.yml` 與多 stage 建置留待日後需要時再啟用。

### 測試

執行前端單元測試：
```bash
cd frontend
pnpm test
```

## 🤝 參與貢獻

我們非常歡迎任何形式的貢獻！無論是回報 Bug、提出新功能建議，或是直接提交 PR。

1. Fork 本專案
2. 建立您的 Feature Branch (`git checkout -b feature/AmazingFeature`)
3. 提交您的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 [MIT License](LICENSE) 授權。
