# Quick Tips Reference

A collection of helpful reminders for common tasks and procedures.

## Development Environment

### Starting the API
```bash
# From the root directory
./scripts/start_api.sh
```

### Starting the Realtime Client
```bash
# From the //src/realtime_client directory
pnpm run dev
```

Alternatively:
```bash
# From any directory
./scripts/rebuild.sh
```

**Note:** Use the rebuild script if you have not run the fetch_latest script. This is an alternative way to ensure your environment is up to date.

### Fetching Latest Documentation
```bash
# From the root directory
./scripts/fetch_latest.sh
```

**Note:** This script CURRENTLY runs just `git pull` internally. However, the upstream release_1.0-pre branch is currently being worked on due to a couple of bugs causing errors. The script may need to be updated to `git pull upstream release_1.0-pre` when that branch is ready.

---
*Last Updated: October 7, 2025*