#!/bin/bash

# Frontend multi-app startup script for YA-PapersWithCode
# - Scans each subfolder in frontend/ for package.json
# - Installs deps if needed
# - Starts each app on its own port (default base 5173, incrementing)
# - Gracefully stops all on exit (Ctrl+C)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FRONTEND_ROOT="$SCRIPT_DIR/frontend"

# Options
INSTALL_ONLY="${INSTALL_ONLY:-false}"   # set INSTALL_ONLY=true to skip starting dev servers
PORT_BASE="${PORT_BASE:-5173}"          # set PORT_BASE to change starting port

log_info "Working directory: $FRONTEND_ROOT"

# Pre-flight: Node and npm
if ! command -v node >/dev/null 2>&1; then
  log_error "Node.js is not installed."
  echo "Install via Homebrew: brew install node"
  echo "Or from: https://nodejs.org/"
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  log_error "npm is not installed."
  echo "Install npm: https://www.npmjs.com/get-npm"
  exit 1
fi
log_info "Node.js version: $(node -v)"
log_info "npm version: $(npm -v)"

# Backend health check (optional)
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
  log_warn "Backend API server not detected at http://localhost:8000"
  log_warn "Run ./start_backend.sh in another terminal if needed."
else
  log_info "Backend API server is running at http://localhost:8000"
fi

# Discover frontend projects (portable, no 'mapfile')
APP_DIRS=()
if [ -d "$FRONTEND_ROOT" ]; then
  for dir in "$FRONTEND_ROOT"/*/; do
    [ -d "$dir" ] || continue
    dir="${dir%/}"
    if [ -f "$dir/package.json" ]; then
      APP_DIRS+=("$dir")
    fi
  done
fi

if [ "${#APP_DIRS[@]}" -eq 0 ]; then
  log_warn "No apps found. Put apps under $FRONTEND_ROOT/<app> with a package.json."
  exit 0
fi

# Helper: does package.json contain scripts.dev?
has_dev_script() {
  node -e "try{const p=require('$1/package.json'); process.exit(p.scripts&&p.scripts.dev?0:1)}catch(e){process.exit(1)}" >/dev/null 2>&1
}

# Track PIDs to cleanup on exit
PIDS=()
NAMES=()
PORTS=()

cleanup() {
  if [ "${#PIDS[@]}" -gt 0 ]; then
    echo
    log_info "Stopping ${#PIDS[@]} frontend process(es)..."
    for pid in "${PIDS[@]}"; do
      kill "$pid" 2>/dev/null || true
    done
    wait || true
  fi
}
trap cleanup EXIT INT TERM

# Start each app
CURRENT_PORT="$PORT_BASE"
INDEX=1

for app_dir in "${APP_DIRS[@]}"; do
  app_name="$(basename "$app_dir")"
  log_info "==> ${INDEX}. App: $app_name"

  pushd "$app_dir" >/dev/null

  # Install deps if needed
  if [ ! -d "node_modules" ]; then
    log_info "Installing dependencies in $app_name..."
    if [ -f "package-lock.json" ]; then
      npm ci
    else
      npm install
    fi
  else
    if [ "package.json" -nt "node_modules" ]; then
      log_warn "package.json changed in $app_name. Updating dependencies..."
      npm install
    else
      log_info "Dependencies are up to date for $app_name."
    fi
  fi

  if [ "$INSTALL_ONLY" = "true" ]; then
    log_info "Install-only mode: skipping dev server for $app_name."
    popd >/dev/null
    INDEX=$((INDEX+1))
    continue
  fi

  # Choose port; increment until free
  while lsof -Pi :"$CURRENT_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; do
    CURRENT_PORT=$((CURRENT_PORT+1))
  done

  if has_dev_script "$app_dir"; then
    log_info "Starting '$app_name' via 'npm run dev' on port $CURRENT_PORT..."
    npm run dev -- --port "$CURRENT_PORT" >/dev/null 2>&1 &
  else
    log_warn "No 'dev' script found for $app_name. Using 'npx vite' fallback on port $CURRENT_PORT..."
    npx vite --port "$CURRENT_PORT" >/dev/null 2>&1 &
  fi

  pid=$!
  PIDS+=("$pid")
  NAMES+=("$app_name")
  PORTS+=("$CURRENT_PORT")

  log_info "Started $app_name (pid $pid) at http://localhost:$CURRENT_PORT"

  CURRENT_PORT=$((CURRENT_PORT+1))
  popd >/dev/null
  INDEX=$((INDEX+1))
done

if [ "${#PIDS[@]}" -gt 0 ]; then
  echo
  echo "=== Frontend Dev Servers ==="
  for i in "${!PIDS[@]}"; do
    echo "- ${NAMES[$i]}: http://localhost:${PORTS[$i]}  (pid ${PIDS[$i]})"
  done
  echo
  echo "Press Ctrl+C to stop all."
  wait
else
  log_warn "No dev servers started (INSTALL_ONLY=true?)."
fi