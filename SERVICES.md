# Service Management Quick Reference

## Quick Start

```bash
# See all available commands
make help

# Start services
make service-up

# Check status
make service-status

# Stop services
make service-down
```

## Main Commands

| Command | Description |
|---------|-------------|
| `make service-up` | Start all services |
| `make service-down` | Stop all services |
| `make service-restart` | Restart all services |
| `make service-status` | Show status of all services |
| `make service-logs` | Follow logs from all services |

## Redis Commands

| Command | Description |
|---------|-------------|
| `make redis-up` | Start Redis only |
| `make redis-down` | Stop Redis only |
| `make redis-status` | Show Redis status and stats |
| `make redis-logs` | Show Redis logs |
| `make redis-cli` | Open interactive Redis CLI |

## Utility

| Command | Description |
|---------|-------------|
| `make clean` | Stop all services and remove volumes |
| `make help` | Show all available commands |

---

**Note:** The bash dashboard in `dashboard/` is deprecated. Use `make` commands instead.
