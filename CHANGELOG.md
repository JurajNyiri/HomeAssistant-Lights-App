# Changelog

## Unreleased
- Coordinator refresh writes now run only when state, mode, or brightness updates are pending, so BLE commands are sent exclusively when data needs syncing and no longer trigger periodic flickers.
- After a disconnect, state, mode, and brightness are flagged as pending so the next reconnect performs a one-time refresh to restore entity data without introducing constant polling writes.
