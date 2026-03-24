# 📘 PostgreSQL Schema & Migration 交接文件（課程系統）

## 🧭 專案目的

本資料庫設計用於「課程查詢系統」，支援：

* 高頻查詢（選課、搜尋）
* 複雜邏輯（衝堂檢查）
* 可維護 ETL（學校資料同步）

採用設計：

* 正規化（Normalized Schema）
* 多對多關聯表
* 結構化時間欄位
* 分階段 Migration + ETL

---

# 🏗️ Migration 概覽

目前共有 **6 個 Alembic migrations（尚未執行）**

| Migration | Revision       | 說明                        |
| --------- | -------------- | ------------------------- |
| M1        | `50b6a42940f4` | 建立核心表（無 FK）               |
| M2        | `c006c0ea1911` | 建立 courses + ENUM         |
| M3        | `353b43253264` | 建立關聯表（無 FK）               |
| M4        | `e2f220a299e5` | 加入全部 FK + CASCADE         |
| M5        | `a247ff1100bf` | 建立 index（CONCURRENTLY）    |
| M6        | `a478b363ef7f` | 建立 metadata 表（ETL 時間戳記）   |

---

# 🚀 Migration + ETL 執行流程（⚠️ 必看）

## 🪜 Step 1：執行 Migration 1

```bash
uv run alembic -c alembic.ini upgrade 50b6a42940f4
```

### 📥 匯入資料

* colleges
* departments
* teachers

### 📌 說明

* 此階段尚未有 FK
* 可安全進行 bulk insert

---

## 🪜 Step 2：執行 Migration 2

```bash
uv run alembic -c alembic.ini upgrade c006c0ea1911
```

### 📥 匯入資料

* courses

### ⚠️ 注意

* `course_type` 必須符合 ENUM（REQUIRED / ELECTIVE）
* `class_no` 為 UNIQUE，不可重複

---

## 🪜 Step 3：執行 Migration 3

```bash
uv run alembic -c alembic.ini upgrade 353b43253264
```

### 📥 匯入資料（關聯資料）

* course_teachers
* course_times
* course_departments
* course_colleges

### 📌 說明

* 尚未有 FK → 可先匯入不完整資料（方便 ETL）
* teachers 需先去重

---

## 🪜 Step 4：資料清洗（🔥關鍵步驟）

在執行 FK 前，務必檢查：

```sql
-- orphan course_teachers
SELECT *
FROM course_teachers ct
LEFT JOIN courses c ON ct.course_id = c.id
WHERE c.id IS NULL;
```

```sql
-- orphan departments
SELECT *
FROM course_departments cd
LEFT JOIN departments d ON cd.department_id = d.id
WHERE d.id IS NULL;
```

```sql
-- orphan course_colleges
SELECT *
FROM course_colleges cc
LEFT JOIN courses c ON cc.course_id = c.id
WHERE c.id IS NULL;

SELECT *
FROM course_colleges cc
LEFT JOIN colleges col ON cc.college_id = col.id
WHERE col.id IS NULL;
```

### ⚠️ 若有資料錯誤

👉 必須先修正，否則 Migration 4 會失敗

---

## 🪜 Step 5：執行 Migration 4（加入 FK）

```bash
uv run alembic -c alembic.ini upgrade e2f220a299e5
```

### 📌 說明

* 開始 enforce referential integrity
* 全部 FK 均加入 `ON DELETE CASCADE`，涵蓋：
  * `departments → colleges`
  * `course_teachers → courses, teachers`
  * `course_times → courses`
  * `course_departments → courses, departments`
  * `course_colleges → courses, colleges`

### ⚠️ 風險

* 若資料不乾淨 → migration 會 fail

---

## 🪜 Step 6：執行 Migration 5（Index）

```bash
uv run alembic -c alembic.ini upgrade a247ff1100bf
```

### 📌 說明

* 使用 `CREATE INDEX CONCURRENTLY`
* 避免鎖表（production 必備）

### ⚠️ 注意

* 不可包在 transaction 中（Alembic 已處理）

---

## 🪜 Step 7：執行 Migration 6（Metadata）

```bash
uv run alembic -c alembic.ini upgrade a478b363ef7f
```

### 📌 說明

* 建立 `metadata` 表（單列限制，`CHECK id = 1`）
* 用於記錄最後一次 ETL 同步時間（`last_update_time`）
* ETL 完成後手動 UPDATE 此欄位供前端或排程查詢

---

# 🧠 資料匯入設計（ETL）

## ⚠️ 原則（非常重要）

❌ 不可直接 insert JSON → production tables
✅ 必須經過 staging + transform

---

## 🏗️ ETL 流程

```text
JSON → staging table → 清洗 → insert → relations → validate
```

---

## 📌 關鍵處理

### 1️⃣ teachers 去重

```sql
INSERT INTO teachers (name)
SELECT DISTINCT ...
ON CONFLICT DO NOTHING;
```

---

### 2️⃣ class_times 解析

```text
"1-A" → day=1, period=A
```

---

### 3️⃣ 多對多關聯

使用：

```sql
unnest()
CROSS JOIN LATERAL
```

---

# ⚠️ 常見錯誤（請避免）

## ❌ 1. 提前加 FK

→ 匯入會失敗

## ❌ 2. 提前建 index

→ bulk insert 變慢

## ❌ 3. 不做資料清洗

→ migration 4 直接炸

## ❌ 4. teachers 未去重

→ 重複資料爆炸

---

# 🧩 系統設計特點

## ✅ 優點

* 高效查詢（index）
* 支援衝堂分析（結構化時間）
* 易於維護（分階段 migration）
* 資料安全（constraints + FK）

---

# 🔧 未來擴展建議

## 🚀 建議新增

### 1️⃣ semester（學期）

避免資料被覆蓋

---

### 2️⃣ enrollment（選課）

```text
student ↔ course
```

---

### 3️⃣ cache（Redis）

熱門查詢加速

---

### 4️⃣ search（全文搜尋）

Postgres GIN / Elastic

---

# 🎯 最後提醒（給接手工程師）

👉 請務必遵守：

1. **Migration ≠ Data Import**
2. **先 schema → 再 data → 再 constraint**
3. **任何 FK 問題 → 回到資料清洗，不要硬改 schema**

---

# 📌 快速指令總覽

```bash
# run specific migration
uv run alembic -c alembic.ini upgrade <revision>

# run all
uv run alembic -c alembic.ini upgrade head

# rollback
uv run alembic -c alembic.ini downgrade -1
```

---

# 🙌 結語

這套設計已達：

✅ Production-ready
✅ 易維護 ETL pipeline

如需擴展（選課系統 / 即時搶課 / 分散式架構），請再進一步設計。

---
