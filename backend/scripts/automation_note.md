# Automation 想法

## 希望之後以下流程之後要自動化

抓 portal 課程 -> (`all.json`) -> `extract_from_json.py` -> (一堆 *.sql) -> 加入 DB


## 現在的做法（手動一鍵自動化）

### 前置條件

1. Docker postgres 已啟動：`docker compose up db -d`
2. 已產生 seed SQL 檔案（若尚未產生，先執行 Step 1）

### Step 1：產生 seed SQL（如果 `seeds/` 已有檔案可跳過）

```bash
cd backend/scripts
uv run extract_from_json.py --input all.json --out-dir ./seeds
```

### Step 2：執行 migration + seed 一鍵腳本

依你的作業系統選擇對應的腳本：

#### Linux / macOS（Bash）

```bash
chmod +x migrate_and_seed.sh
./migrate_and_seed.sh
```

#### Windows（PowerShell）

```powershell
powershell -ExecutionPolicy Bypass -File migrate_and_seed.ps1
```

> **Windows 注意事項：**
> - 需要 PowerShell 5.1+（Windows 10/11 內建）或 PowerShell 7+
> - 如果遇到執行原則 (Execution Policy) 限制，可用 `-ExecutionPolicy Bypass` 旗標
> - `migrate_and_seed.sh` 也可以在 Git Bash 或 WSL 下執行

#### 系統相容性總覽

| 腳本                     | Linux | macOS | Windows (PowerShell) | Windows (Git Bash / WSL) |
| ------------------------ | :---: | :---: | :------------------: | :----------------------: |
| `migrate_and_seed.sh`    |  ✅   |  ✅   |          ❌          |            ✅            |
| `migrate_and_seed.ps1`   |  ❌   |  ❌   |          ✅          |            ❌            |

此腳本會依照正確順序自動執行：

1. **M1** → 建立核心表 → seed colleges、departments、teachers
2. **M2** → 建立 courses + ENUM → seed courses
3. **M3** → 建立關聯表 → seed course_relations
4. **M4** → 加入 FK constraints（資料已到位，不會失敗）
5. **M5** → 建立 indexes
6. **M6** → 建立 metadata 表

### 環境變數（可選覆蓋）

| 變數          | 預設值       | 說明         |
| ------------- | ------------ | ------------ |
| `DB_HOST`     | `127.0.0.1`  | 資料庫主機   |
| `DB_PORT`     | `5432`       | 資料庫埠號   |
| `DB_USER`     | `postgres`   | 資料庫使用者 |
| `DB_PASSWORD` | `postgres`   | 資料庫密碼   |
| `DB_NAME`     | `ncu_tldr`   | 資料庫名稱   |

---

## 舊的做法（手動，已不建議）

Step 1:
```
uv run extract_from_json.py --input all.json --out-dir ./seeds     # 會得到一堆 .sql
```

Step 2:
手動去 DB 執行 SQL
