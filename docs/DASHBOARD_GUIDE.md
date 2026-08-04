# Dashboard guide

Run `bughunter-dashboard payload.json` to serve a read-only dashboard at `http://127.0.0.1:8765`. Use `--host` and `--port` to change the bind address. It displays existing payload data only; it never initiates a scan.

With Docker Compose, first generate `artifacts/payload.json` using the scanner service, then run `docker compose up dashboard` and open `http://localhost:8765`.
