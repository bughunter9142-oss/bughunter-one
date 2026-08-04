# User guide

Run `bughunter-one https://example.com --output payload.json --reports-dir reports` to create a passive scan payload and reports. Use `--config bughunter.toml` for repeatable scan settings and `--debug` for JSON-line debug logs. View an existing result with `bughunter-dashboard payload.json`; the dashboard reads JSON only and never starts reconnaissance.

Use `docker compose run --rm scanner` to write sample artifacts to `artifacts/`, then `docker compose up dashboard` to expose them at port 8765.
