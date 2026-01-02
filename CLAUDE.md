# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **customized fork** of the official [frappe/frappe_docker](https://github.com/frappe/frappe_docker) repository. This fork has been modified to provide containerized deployments specifically for the **Frappe framework only** (without ERPNext).

### Key Modifications from Original

1. **Removed ERPNext** - All ERPNext-specific configurations, images, and references have been removed
2. **Custom Frappe Repository** - Uses [adam7seven/frappe](https://github.com/adam7seven/frappe) instead of the official frappe/frappe
3. **Custom Docker Registry** - Uses `adam7` registry instead of `frappe` for images
4. **Focused on Frappe** - Optimized for pure Frappe framework deployments without ERPNext dependencies

## Repository Structure

```
frappe_docker/
├── images/                    # Docker image definitions
│   ├── production/           # Multi-stage production builds
│   ├── custom/               # Custom app image builds
│   └── layered/              # Layered architecture images
├── development/              # Development environment setup
│   ├── installer.py          # Automated bench/site setup script
│   ├── apps-example.json     # Example apps configuration
│   └── vscode-example/       # VS Code debug configuration
├── docs/                     # Comprehensive documentation
├── overrides/                # Docker Compose override files
├── tests/                    # Integration tests (pytest)
├── .github/workflows/        # CI/CD pipelines
├── compose.yaml              # Main compose template
├── pwd.yml                   # Play-with-Docker setup
├── docker-bake.hcl           # Docker Buildx Bake definitions
└── example.env               # Environment variables template
```

## Common Development Commands

### Building Images

**Using Docker Buildx Bake (recommended):**
```bash
# Build all default targets (frappe, base, build)
docker buildx bake

# Build specific version
FRAPPE_VERSION=v15.90.1 docker buildx bake

# Build for ARM64 architecture
docker buildx bake --no-cache --set "*.platform=linux/arm64"

# Build individual targets
docker buildx bake frappe
docker buildx bake bench
docker buildx bake base
```

**Image Registry and Repository:**
- **Registry**: `adam7` (custom registry, not `frappe`)
- **Frappe Repository**: Uses [adam7seven/frappe](https://github.com/adam7seven/frappe) (custom fork, not official `frappe/frappe`)
- **Image Tags**: `adam7/frappe:${FRAPPE_VERSION}` (e.g., `adam7/frappe:v15.90.1`)

Available build targets (defined in `docker-bake.hcl:33-103`):
- `bench` - Frappe Bench management tool
- `frappe` - Main Frappe application image (Frappe-only, no ERPNext)
- `base` - Base image with dependencies
- `build` - Build stage for compilation
- `bench-test` - Testing variant of bench image

### Running Containers

**Quick Start (Play with Docker):**
```bash
docker compose -f pwd.yml up -d
```

**Development Environment:**
```bash
# Copy environment template
cp example.env .env

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

### Development Setup

**Automated Setup (using installer.py):**
```bash
# Run installer to create bench and site
python3 development/installer.py \
  --apps-json apps.json \
  --bench-name frappe-bench \
  --site-name development.localhost \
  --frappe-branch version-15 \
  --db-type postgres

# For MariaDB
python3 development/installer.py \
  --db-type mariadb
```

**Manual Setup:**
```bash
# Initialize bench
bench init --skip-redis-config-generation frappe-bench --frappe-branch version-15

cd frappe-bench

# Configure database
bench set-config -g db_host mariadb
bench set-config -g redis_cache "redis://redis-cache:6379"
bench set-config -g redis_queue "redis://redis-queue:6379"

# Create site
bench new-site --admin-password=admin --db-type=mariadb frontend
```

### Linting and Code Quality

**Pre-commit hooks:**
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run all files
pre-commit run --all-files

# Run specific hook
pre-commit run trailing-whitespace
```

### Testing

**Setup test environment:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt

# Run tests
pytest

# Run specific test
pytest tests/test_frappe_docker.py

# Run with verbose output
pytest -v
```

**Available tests:**
- `test_frappe_docker.py` - Main integration tests
- `_check_connections.py` - Connection validation
- `_check_website_theme.py` - Theme verification
- `_create_bucket.py` - S3 bucket creation
- `_ping_frappe_connections.py` - Health checks

## Architecture

### Container Orchestration

The system uses a multi-container architecture with Docker Compose:

1. **Backend Services** (`compose.yaml:45-91`):
   - `backend` - Main Frappe application server (Python/WSGI)
   - `configurator` - One-time configuration service
   - `websocket` - Real-time WebSocket server (Node.js)

2. **Frontend** (`compose.yaml:49-67`):
   - `frontend` - Nginx reverse proxy and static file server

3. **Background Processing** (`compose.yaml:78-91`):
   - `queue-short` - Short task worker
   - `queue-long` - Long-running task worker
   - `scheduler` - Scheduled task runner

4. **Data Services**:
   - `db` - PostgreSQL or MariaDB database
   - `redis-cache` - Redis for caching
   - `redis-queue` - Redis for job queues

### Image Build Strategy

The project uses a multi-stage Docker build approach (`images/production/Containerfile`):

1. **Base Stage** - Debian bookworm with Python 3.11.6 and Node.js 20.19.2
2. **Build Stage** - Dependencies and compilation
3. **Frappe Stage** - Frappe framework installation
4. **Production Stage** - Final optimized image

### Custom Applications

**Note**: This fork is **Frappe-only** and does not include ERPNext by default.

Apps are configured via `apps.json`:
```json
[
  {
    "url": "https://github.com/adam7seven/srm.git",
    "branch": "main"
  }
]
```

Custom apps can be:
- Built into custom images using `images/custom/Containerfile`
- Mounted at runtime via volumes

**ERPNext**: If you need ERPNext, you would need to:
1. Add ERPNext to `apps.json`
2. Update the Frappe repository back to the official one
3. Modify the build configuration to include ERPNext components

This fork is specifically designed for Frappe-only deployments.

### Service Dependencies

The configurator service (`compose.yaml:20-43`) runs first to generate `sites/apps.txt` and set up Redis/database configuration. All backend services depend on it completing successfully.

## Environment Configuration

Key environment variables (see `example.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `FRAPPE_VERSION` | Frappe branch/version | `develop` |
| `CUSTOM_IMAGE` | Custom image repository | `adam7/frappe` |
| `CUSTOM_TAG` | Image tag | `$FRAPPE_VERSION` |
| `DB_HOST` | Database host | Service name |
| `DB_PORT` | Database port | `5432`/`3306` |
| `REDIS_CACHE` | Redis cache URL | `redis-cache:6379` |
| `REDIS_QUEUE` | Redis queue URL | `redis-queue:6379` |
| `PULL_POLICY` | Image pull policy | `always` |
| `RESTART_POLICY` | Container restart policy | `unless-stopped` |

**Important**: This fork uses custom defaults:
- **Registry**: `adam7` (not `frappe`)
- **Frappe Repo**: `https://github.com/adam7seven/frappe` (not `https://github.com/frappe/frappe`)
- **ERPNext**: Not included by default

## Development Workflow

### VS Code Dev Containers

The recommended development approach uses VS Code Dev Containers:

1. Copy devcontainer config:
   ```bash
   cp -R devcontainer-example .devcontainer
   cp -R development/vscode-example development/.vscode
   ```

2. Open in VS Code and rebuild in container

3. All development happens inside the container

4. Benches should be created in the mounted `development/` directory

### Database Selection

Choose between MariaDB (default) or PostgreSQL:

**MariaDB** (default in `pwd.yml`):
- Commented out in `pwd.yml:95-115`
- Port 3306
- User: root, Password: admin

**PostgreSQL** (active in `pwd.yml:79-93`):
- Port 5432
- User: postgres, Password: admin

### Multi-Architecture Support

ARM64 builds require:
```bash
docker buildx bake --no-cache --set "*.platform=linux/arm64"
```

Then update `pwd.yml`:
- Add `platform: linux/arm64` to all services
- Use `:latest` tag for images

## CI/CD Pipeline

GitHub Actions workflows (`.github/workflows/`):

- `build_stable.yml` - Builds and pushes stable releases
- `build_apps.yml` - Builds custom app images
- `docker-build-push.yml` - Generic build and push
- `lint.yml` - Pre-commit linting
- `pre-commit-autoupdate.yml` - Auto-update pre-commit hooks

Builds are triggered on:
- Push to main branch
- Version tags (v*, version-*)
- Manual dispatch

## Testing Strategy

Integration tests use pytest with:

1. **Compose Validation** (`compose.ci.yaml`):
   - Minimal test environment
   - Fast startup for CI

2. **Health Checks**:
   - Database connectivity
   - Redis availability
   - Service readiness

3. **Functional Tests**:
   - Site creation
   - App installation
   - API endpoints

Test files are in `tests/` directory with helper utilities in `utils.py`.

## Troubleshooting

### Container Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs backend
docker compose logs -f create-site

# Follow logs
docker compose logs -f
```

### Common Issues

1. **Database Connection**:
   - Check `DB_HOST` matches service name
   - Verify health checks pass: `docker compose ps`

2. **Redis Connection**:
   - Ensure `REDIS_CACHE` and `REDIS_QUEUE` are correctly set
   - Check Redis services: `docker compose logs redis-cache`

3. **Site Creation Fails**:
   - Wait for configurator: `docker compose logs configurator`
   - Check database is ready: `docker compose logs db`

4. **Image Build Fails**:
   - Check network connectivity (git clones)
   - Verify Python/Node versions in `docker-bake.hcl`
   - Try: `docker buildx bake --no-cache`

### Development Tips

- Use `development/installer.py` for quick bench/site setup
- Mount `development/` directory for persistent benches
- Use VS Code Dev Containers for consistent environment
- Check `docs/` directory for detailed guides
- Use `bench` commands inside the backend container
- For custom apps, update `apps.json` and rebuild image

## Key Files Reference

- **compose.yaml** - Main service definitions and templates
- **pwd.yml** - Quick demo/playground setup
- **docker-bake.hcl** - Build configuration and targets (uses custom registry and repo)
- **development/installer.py** - Automated development setup
- **example.env** - All configurable environment variables
- **images/production/Containerfile** - Multi-stage build definition (Frappe-only)
- **tests/** - Integration test suite
- **docs/** - Comprehensive documentation (some legacy ERPNext references remain)

## Fork-Specific Notes

This repository is a **customized fork** with the following characteristics:

### What's Different
- **Registry**: Uses `adam7` Docker Hub namespace
- **Frappe Source**: Uses `adam7seven/frappe` repository
- **ERPNext**: Completely removed from default configuration
- **Focus**: Optimized for Frappe-only deployments

### Configuration Files
- `docker-bake.hcl:4-29` - Registry and repository configuration
- `compose.yaml:5` - Custom image reference using `adam7` registry
- `apps.json` - Custom apps configuration (example: `adam7seven/srm`)

### Migration from Original
If migrating from the original `frappe/frappe_docker`:
1. Update image references from `frappe/*` to `adam7/*`
2. Update `FRAPPE_REPO` environment variable
3. Remove any ERPNext-specific configurations
4. Rebuild images using the custom registry
