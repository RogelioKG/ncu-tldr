#!/usr/bin/env bash
# migrate_and_seed.sh
# Runs Alembic migrations 1-6 and seeds data at the correct stages.
#
# Usage:
#   cd backend
#   bash scripts/migrate_and_seed.sh
#
# Prerequisites:
#   - Docker postgres is running (docker compose up db)
#   - uv is installed
#   - psql client is available (or uses docker exec as fallback)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEEDS_DIR="$SCRIPT_DIR/seeds"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$BACKEND_DIR/.." && pwd)"

# DB connection defaults (override via env vars)
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_NAME="${DB_NAME:-ncu_tldr}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---------- helpers ----------

run_migration() {
    local revision="$1"
    local description="$2"
    info "Running migration: $description (revision: $revision)"
    cd "$BACKEND_DIR"
    uv run alembic -c alembic.ini upgrade "$revision"
    info "Migration $description completed."
}

run_sql_file() {
    local sql_file="$1"
    local filename
    filename="$(basename "$sql_file")"

    if [ ! -f "$sql_file" ]; then
        error "Seed file not found: $sql_file"
    fi

    info "Seeding: $filename"

    # Try psql directly first, fall back to docker exec
    if command -v psql &> /dev/null; then
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$sql_file"
    else
        warn "psql not found locally, using docker exec..."
        local container
        container=$(docker compose -f "$ROOT_DIR/docker-compose.yml" -f "$ROOT_DIR/docker-compose.dev.yml" ps -q db 2>/dev/null || docker compose ps -q db 2>/dev/null)
        if [ -z "$container" ]; then
            error "Cannot find running db container. Is 'docker compose up db' running?"
        fi
        docker exec -i "$container" psql -U "$DB_USER" -d "$DB_NAME" < "$sql_file"
    fi

    info "Seeded: $filename"
}

# ---------- pre-flight checks ----------

info "=== Pre-flight checks ==="

cd "$BACKEND_DIR"

if [ ! -f "alembic.ini" ]; then
    error "alembic.ini not found. Please run this script from the backend directory or check your setup."
fi

# Verify seed files exist
for f in colleges_seed.generated.sql departments_seed.generated.sql teachers_seed.generated.sql \
         courses_seed.generated.sql course_relations_seed.generated.sql metadata_seed.generated.sql; do
    if [ ! -f "$SEEDS_DIR/$f" ]; then
        error "Missing seed file: $SEEDS_DIR/$f — run extract_from_json.py first."
    fi
done

info "All seed files found. Starting migration + seed pipeline...\n"

# ============================================================
# Step 1: Migration 1 — core tables (no FK)
# ============================================================
run_migration "50b6a42940f4" "M1: core tables (colleges, departments, teachers)"

# Seed: colleges, departments, teachers
run_sql_file "$SEEDS_DIR/colleges_seed.generated.sql"
run_sql_file "$SEEDS_DIR/departments_seed.generated.sql"
run_sql_file "$SEEDS_DIR/teachers_seed.generated.sql"

# ============================================================
# Step 2: Migration 2 — courses + ENUM
# ============================================================
run_migration "c006c0ea1911" "M2: courses table + ENUM"

# Seed: courses
run_sql_file "$SEEDS_DIR/courses_seed.generated.sql"

# ============================================================
# Step 3: Migration 3 — relation tables (no FK)
# ============================================================
run_migration "353b43253264" "M3: relation tables (course_teachers, course_times, etc.)"

# Seed: all relation data
run_sql_file "$SEEDS_DIR/course_relations_seed.generated.sql"

# ============================================================
# Step 4: Migration 4 — add FK constraints
# ============================================================
info "All data seeded. Adding FK constraints..."
run_migration "e2f220a299e5" "M4: add all FK + CASCADE"

# ============================================================
# Step 5: Migration 5 — indexes (CONCURRENTLY)
# ============================================================
run_migration "a247ff1100bf" "M5: create indexes"

# ============================================================
# Step 6: Migration 6 — metadata table
# ============================================================
run_migration "a478b363ef7f" "M6: metadata table"

# Seed: metadata (version + last_update_time)
run_sql_file "$SEEDS_DIR/metadata_seed.generated.sql"

# ============================================================
echo ""
info "=== All migrations and seeds completed successfully! ==="
