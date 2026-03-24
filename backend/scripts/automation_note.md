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

```bash
cd backend
bash scripts/migrate_and_seed.sh
```

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
| `DB_HOST`     | `localhost`  | 資料庫主機   |
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
