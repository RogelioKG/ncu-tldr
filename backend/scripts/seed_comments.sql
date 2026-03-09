-- 留言與留言投票測試資料（手動測試前後端與 DB 連動用）
--
-- 使用方式：
--   1. 先執行 alembic upgrade head
--   2. 確保至少有 1 筆 users、course_id = 1 的 courses（若無，見下方「可選：最小依賴」）
--   3. psql $DATABASE_URL -f backend/scripts/seed_comments.sql
--
-- 若 DB 為空，可先執行「可選：最小依賴」再執行本檔。

-- ============================================================
-- 可選：最小依賴（僅在 users / departments / teachers / courses 皆無資料時執行）
-- ============================================================
/*
INSERT INTO departments (name, code) VALUES ('資訊工程學系', 'CS');
INSERT INTO teachers (name, department_id) VALUES ('王大明', 1);
INSERT INTO courses (department_id, teacher_id, course_code, name, credits, course_type)
VALUES (1, 1, 'CS3001', '演算法', 3, '必修');
INSERT INTO users (email, display_name) VALUES ('seed@test.local', 'Seed 測試用戶');
*/

-- ============================================================
-- 根留言（3 則，course_id = 1）
-- ============================================================
WITH seed_user AS (SELECT id FROM users LIMIT 1),
     seed_course AS (SELECT id FROM courses WHERE id = 1 LIMIT 1)
INSERT INTO comments (course_id, user_id, parent_id, title, content, likes, dislikes)
SELECT
  c.id,
  u.id,
  NULL,
  v.title,
  v.content,
  v.likes,
  v.dislikes
FROM seed_course c
CROSS JOIN seed_user u
CROSS JOIN (VALUES
  ('老師教得很好。', '老師教得很好，作業有點多，但學到很多！', 12, 1),
  ('考試很幾，要認真準備。', '期中考範圍很廣，要提早開始複習，建議把作業都弄懂。', 8, 0),
  ('分組報告很重要', '找到好組員很關鍵，報告佔比不少，老師對報告品質要求高。', 5, 2)
) AS v(title, content, likes, dislikes);

-- ============================================================
-- 回覆（對應剛插入的 3 個根留言：1-1, 2-1, 3-1 各一則）
-- ============================================================
WITH seed_user AS (SELECT id FROM users LIMIT 1),
     roots AS (
       SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
       FROM comments
       WHERE course_id = 1 AND parent_id IS NULL
       ORDER BY id
       LIMIT 3
     )
INSERT INTO comments (course_id, user_id, parent_id, title, content, likes, dislikes)
SELECT
  1,
  u.id,
  r.id,
  v.title,
  v.content,
  v.likes,
  v.dislikes
FROM seed_user u
CROSS JOIN (VALUES
  (1, '回覆 User1', '同意，作業真的很多但很有收穫。', 2, 0),
  (2, '回覆 User3', '組員真的很重要，建議開學就找好。', 1, 0),
  (3, '回覆 User3', '報告佔 40% 要提早準備。', 0, 0)
) AS v(rn, title, content, likes, dislikes)
JOIN roots r ON r.rn = v.rn;

-- ============================================================
-- 可選：留言投票（1 = 讚, -1 = 倒讚）
-- ============================================================
/*
WITH seed_user AS (SELECT id FROM users LIMIT 1),
     first_three AS (
       SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
       FROM comments WHERE course_id = 1 ORDER BY id LIMIT 3
     )
INSERT INTO comment_votes (user_id, comment_id, vote_type)
SELECT u.id, f.id, v.vote_type
FROM seed_user u
JOIN first_three f ON f.rn = v.rn
CROSS JOIN (VALUES (1, 1), (2, 1), (3, -1)) AS v(rn, vote_type)
ON CONFLICT (user_id, comment_id) DO NOTHING;
*/
