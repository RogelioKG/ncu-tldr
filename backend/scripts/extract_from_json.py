import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

_VALID_COURSE_TYPES = frozenset({"REQUIRED", "ELECTIVE"})


def _sql_text(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    s = s.replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"


def _sql_values_rows(rows: Iterable[Iterable[Any]]) -> str:
    rendered = []
    for row in rows:
        rendered.append("(" + ", ".join(_sql_text(v) for v in row) + ")")
    return ",\n  ".join(rendered)


def _parse_day_period(token: str) -> tuple[int | None, str | None]:
    token = (token or "").strip()
    if not token:
        return None, None
    if "-" not in token:
        return None, token
    day_s, period = token.split("-", 1)
    day_s = day_s.strip()
    period = period.strip()
    try:
        day = int(day_s)
    except ValueError:
        day = None
    return day, period or None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract seed SQL files from courses_data.json for migration-ordered imports."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to courses_data.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Output directory for generated .sql files",
    )
    args = parser.parse_args()

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    courses: list[dict[str, Any]] = raw.get("courses", [])

    teachers_set: set[str] = set()
    for c in courses:
        for t in c.get("teachers", []) or []:
            t = (t or "").strip()
            if t:
                teachers_set.add(t)
    teachers = sorted(teachers_set)

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # M1: teachers
    teachers_sql = (
        "BEGIN;\n\n"
        "INSERT INTO teachers (name)\n"
        "VALUES\n  "
        + _sql_values_rows([[t] for t in teachers])
        + "\nON CONFLICT (name) DO NOTHING;\n\n"
        "COMMIT;\n"
    )
    (out_dir / "teachers_seed.generated.sql").write_text(teachers_sql, encoding="utf-8")

    # M2: courses
    errors: list[str] = []
    course_rows = []
    for c in courses:
        serial_no = c.get("serialNo")
        class_no = c.get("classNo")
        title = c.get("title")
        credit = c.get("credit")
        course_type = c.get("courseType")

        if serial_no is None:
            errors.append(f"course missing serialNo: classNo={class_no!r}")
        if not class_no:
            errors.append(f"course missing classNo: serialNo={serial_no!r}")
        if not title:
            errors.append(f"course missing title: serialNo={serial_no!r}")
        if credit is None:
            errors.append(f"course missing credit: serialNo={serial_no!r}")
        if course_type not in _VALID_COURSE_TYPES:
            errors.append(
                f"course has invalid courseType={course_type!r}: serialNo={serial_no!r}"
            )

        course_rows.append(
            [
                serial_no,
                class_no,
                title,
                credit,
                c.get("passwordCard") or "NONE",
                c.get("limitCnt"),
                c.get("admitCnt") or 0,
                c.get("waitCnt") or 0,
                course_type,
            ]
        )

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"\n{len(errors)} validation error(s) found. Aborting.", file=sys.stderr)
        return 1

    courses_sql = (
        "BEGIN;\n\n"
        "INSERT INTO courses (\n"
        "  external_id,\n"
        "  class_no,\n"
        "  title,\n"
        "  credit,\n"
        "  password_card,\n"
        "  limit_cnt,\n"
        "  admit_cnt,\n"
        "  wait_cnt,\n"
        "  course_type\n"
        ")\n"
        "VALUES\n  "
        + _sql_values_rows(course_rows)
        + "\nON CONFLICT (external_id) DO UPDATE SET\n"
        "  class_no = EXCLUDED.class_no,\n"
        "  title = EXCLUDED.title,\n"
        "  credit = EXCLUDED.credit,\n"
        "  password_card = EXCLUDED.password_card,\n"
        "  limit_cnt = EXCLUDED.limit_cnt,\n"
        "  admit_cnt = EXCLUDED.admit_cnt,\n"
        "  wait_cnt = EXCLUDED.wait_cnt,\n"
        "  course_type = EXCLUDED.course_type,\n"
        "  updated_at = now();\n\n"
        "COMMIT;\n"
    )
    (out_dir / "courses_seed.generated.sql").write_text(courses_sql, encoding="utf-8")

    # M3: relations (no FK yet, but keep it FK-clean by design)
    ct_rows: list[list[Any]] = []
    time_rows: list[list[Any]] = []
    time_seen: set[tuple[Any, int, str]] = set()
    dept_rows: list[list[Any]] = []
    college_rows: list[list[Any]] = []

    for c in courses:
        course_id = c.get("serialNo")
        for i, t in enumerate(c.get("teachers", []) or []):
            t = (t or "").strip()
            if t:
                ct_rows.append([course_id, t, i])

        for tok in c.get("classTimes", []) or []:
            day, period = _parse_day_period(tok)
            if day is not None and period is not None:
                key = (course_id, day, period)
                if key not in time_seen:
                    time_seen.add(key)
                    time_rows.append([course_id, day, period])

        for dept_id in c.get("departmentIds", []) or []:
            dept_id = (dept_id or "").strip()
            if dept_id:
                dept_rows.append([course_id, dept_id])

        for college_id in c.get("collegeIds", []) or []:
            college_id = (college_id or "").strip()
            if college_id:
                college_rows.append([course_id, college_id])

    relations_parts: list[str] = ["BEGIN;\n"]

    if ct_rows:
        relations_parts.append(
            "INSERT INTO course_teachers (course_id, teacher_id, sort_order)\n"
            "SELECT c.id, t.id, v.sort_order\n"
            "FROM (\n"
            "  VALUES\n  "
            + _sql_values_rows(ct_rows)
            + "\n) AS v(course_external_id, teacher_name, sort_order)\n"
            "JOIN courses c ON c.external_id = v.course_external_id\n"
            "JOIN teachers t ON t.name = v.teacher_name\n"
            "ON CONFLICT (course_id, teacher_id) DO UPDATE SET\n"
            "  sort_order = EXCLUDED.sort_order;\n\n"
        )

    if time_rows:
        relations_parts.append(
            "INSERT INTO course_times (course_id, day, period)\n"
            "SELECT c.id, v.day, v.period\n"
            "FROM (\n"
            "  VALUES\n  "
            + _sql_values_rows(time_rows)
            + "\n) AS v(course_external_id, day, period)\n"
            "JOIN courses c ON c.external_id = v.course_external_id\n"
            "ON CONFLICT (course_id, day, period) DO NOTHING;\n\n"
        )

    if dept_rows:
        relations_parts.append(
            "INSERT INTO course_departments (course_id, department_id)\n"
            "SELECT c.id, d.id\n"
            "FROM (\n"
            "  VALUES\n  "
            + _sql_values_rows(dept_rows)
            + "\n) AS v(course_external_id, department_code)\n"
            "JOIN courses c ON c.external_id = v.course_external_id\n"
            "JOIN departments d ON d.code = v.department_code\n"
            "ON CONFLICT (course_id, department_id) DO NOTHING;\n\n"
        )

    if college_rows:
        relations_parts.append(
            "INSERT INTO course_colleges (course_id, college_id)\n"
            "SELECT c.id, col.id\n"
            "FROM (\n"
            "  VALUES\n  "
            + _sql_values_rows(college_rows)
            + "\n) AS v(course_external_id, college_code)\n"
            "JOIN courses c ON c.external_id = v.course_external_id\n"
            "JOIN colleges col ON col.code = v.college_code\n"
            "ON CONFLICT (course_id, college_id) DO NOTHING;\n\n"
        )

    relations_parts.append("COMMIT;\n")
    (out_dir / "course_relations_seed.generated.sql").write_text(
        "".join(relations_parts), encoding="utf-8"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
