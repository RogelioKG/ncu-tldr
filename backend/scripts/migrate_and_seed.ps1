# migrate_and_seed.ps1
# Runs Alembic migrations 1-6 and seeds data at the correct stages.
#
# Usage:
#   cd backend
#   powershell -ExecutionPolicy Bypass -File scripts/migrate_and_seed.ps1
#
# Prerequisites:
#   - Docker postgres is running (docker compose up db)
#   - .env is configured with DATABASE_URL_SYNC
#   - uv is installed
#   - psql client is available (or uses docker exec as fallback)

$ErrorActionPreference = "Stop"

# Force UTF-8 encoding WITHOUT BOM for console output and pipeline to external programs.
# [System.Text.Encoding]::UTF8 includes a BOM (\xEF\xBB\xBF) which causes psql to choke
# on the first SQL statement (e.g. "BEGIN;" becomes "<BOM>BEGIN;" → syntax error).
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
[Console]::InputEncoding  = $Utf8NoBom
[Console]::OutputEncoding = $Utf8NoBom
$OutputEncoding = $Utf8NoBom
# Set code page to UTF-8 (65001) for child processes like psql / docker
chcp 65001 | Out-Null

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SeedsDir = Join-Path $ScriptDir "seeds"
$BackendDir = Split-Path -Parent $ScriptDir

# DB connection defaults (override via env vars)
$DB_HOST     = if ($env:DB_HOST)     { $env:DB_HOST }     else { "localhost" }
$DB_PORT     = if ($env:DB_PORT)     { $env:DB_PORT }     else { "5432" }
$DB_USER     = if ($env:DB_USER)     { $env:DB_USER }     else { "postgres" }
$DB_PASSWORD = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { "postgres" }
$DB_NAME     = if ($env:DB_NAME)     { $env:DB_NAME }     else { "ncu_tldr" }

# ---------- helpers ----------

function Info($msg)  { Write-Host "[INFO]  $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

function Run-Migration {
    param([string]$Revision, [string]$Description)
    Info "Running migration: $Description (revision: $Revision)"
    Set-Location $BackendDir
    uv run alembic -c alembic.ini upgrade $Revision
    if ($LASTEXITCODE -ne 0) { Error "Migration $Description failed." }
    Info "Migration $Description completed."
}

function Run-SqlFile {
    param([string]$SqlFile)
    $Filename = Split-Path -Leaf $SqlFile

    if (-not (Test-Path $SqlFile)) {
        Error "Seed file not found: $SqlFile"
    }

    Info "Seeding: $Filename"

    # Try psql directly first, fall back to docker exec
    # --set ON_ERROR_STOP=1 makes psql return non-zero exit code on SQL errors
    $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
    if ($psqlPath) {
        $env:PGPASSWORD = $DB_PASSWORD
        $env:PGCLIENTENCODING = "UTF8"
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME --set ON_ERROR_STOP=1 -f $SqlFile
        if ($LASTEXITCODE -ne 0) { Error "Seeding $Filename failed." }
    } else {
        Warn "psql not found locally, using docker exec..."
        $container = docker compose ps -q db 2>$null
        if (-not $container) {
            $container = docker-compose ps -q db 2>$null
        }
        if (-not $container) {
            Error "Cannot find running db container. Is 'docker compose up db' running?"
        }
        # Use cmd /c to pipe file content via native redirection, bypassing PowerShell
        # pipeline which prepends a UTF-8 BOM that breaks psql parsing.
        cmd /c "docker exec -i $container psql -U $DB_USER -d $DB_NAME --set ON_ERROR_STOP=1 < `"$SqlFile`""
        if ($LASTEXITCODE -ne 0) { Error "Seeding $Filename failed." }
    }

    Info "Seeded: $Filename"
}

# ---------- pre-flight checks ----------

Info "=== Pre-flight checks ==="

Set-Location $BackendDir

if (-not (Test-Path "alembic.ini")) {
    Error "alembic.ini not found. Please run this script from the backend directory or check your setup."
}

# Verify seed files exist
$seedFiles = @(
    "colleges_seed.generated.sql",
    "departments_seed.generated.sql",
    "teachers_seed.generated.sql",
    "courses_seed.generated.sql",
    "course_relations_seed.generated.sql",
    "metadata_seed.generated.sql"
)

foreach ($f in $seedFiles) {
    $path = Join-Path $SeedsDir $f
    if (-not (Test-Path $path)) {
        Error "Missing seed file: $path — run extract_from_json.py first."
    }
}

Info "All seed files found. Starting migration + seed pipeline..."
Write-Host ""

# ============================================================
# Step 1: Migration 1 — core tables (no FK)
# ============================================================
Run-Migration -Revision "50b6a42940f4" -Description "M1: core tables (colleges, departments, teachers)"

# Seed: colleges, departments, teachers
Run-SqlFile (Join-Path $SeedsDir "colleges_seed.generated.sql")
Run-SqlFile (Join-Path $SeedsDir "departments_seed.generated.sql")
Run-SqlFile (Join-Path $SeedsDir "teachers_seed.generated.sql")

# ============================================================
# Step 2: Migration 2 — courses + ENUM
# ============================================================
Run-Migration -Revision "c006c0ea1911" -Description "M2: courses table + ENUM"

# Seed: courses
Run-SqlFile (Join-Path $SeedsDir "courses_seed.generated.sql")

# ============================================================
# Step 3: Migration 3 — relation tables (no FK)
# ============================================================
Run-Migration -Revision "353b43253264" -Description "M3: relation tables (course_teachers, course_times, etc.)"

# Seed: all relation data
Run-SqlFile (Join-Path $SeedsDir "course_relations_seed.generated.sql")

# ============================================================
# Step 4: Migration 4 — add FK constraints
# ============================================================
Info "All data seeded. Adding FK constraints..."
Run-Migration -Revision "e2f220a299e5" -Description "M4: add all FK + CASCADE"

# ============================================================
# Step 5: Migration 5 — indexes (CONCURRENTLY)
# ============================================================
Run-Migration -Revision "a247ff1100bf" -Description "M5: create indexes"

# ============================================================
# Step 6: Migration 6 — metadata table
# ============================================================
Run-Migration -Revision "a478b363ef7f" -Description "M6: metadata table"

# Seed: metadata (version + last_update_time)
Run-SqlFile (Join-Path $SeedsDir "metadata_seed.generated.sql")

# ============================================================
Write-Host ""
Info "=== All migrations and seeds completed successfully! ==="
