# Dashboard Quick Reference

## Current Usage

### Monitor all components
```bash
./dashboard.sh system monitor
```

### Check system status
```bash
./dashboard.sh system status
```

### Redis operations
```bash
./dashboard.sh redis monitor    # Detailed panel
./dashboard.sh redis status     # One-time check
./dashboard.sh redis start      # Start container
./dashboard.sh redis stop       # Stop container
./dashboard.sh redis info       # Full stats
```

## Adding New Components

The modular structure makes adding components very clean:

1. **Create component module** in `dashboard/lib/`:
```bash
# dashboard/lib/newcomponent.sh
newcomponent_status() {
    # Implementation
}

newcomponent_monitor() {
    # Implementation
}
```

2. **Source the module** in `dashboard/dashboard.sh`:
```bash
source "$SCRIPT_DIR/lib/newcomponent.sh"
```

3. **Add routing** in `dashboard/lib/help.sh`:
```bash
case "$component" in
    # ... existing components ...
    newcomponent)
        case "$action" in
            monitor) newcomponent_monitor ;;
            status) newcomponent_status ;;
        esac
        ;;
esac
```

4. **Update help text** in `show_help()` function

Each component is now in its own file - much cleaner!
