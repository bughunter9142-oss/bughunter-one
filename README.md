# BugHunter One

## Overview

BugHunter One is a lightweight passive-reconnaissance toolkit. It collects publicly available information about a target, creates a structured JSON payload, and generates HTML, Markdown, PDF, and JSON reports.

Its goals are to provide a small, extensible reconnaissance workflow, keep collected results structured and reportable, and avoid exploitation, brute force, authentication bypass, or invasive testing. The project supports Windows, Linux (including Kali), and macOS with Python 3.10 or newer.

## Features

### Phase 1

- Package-based project structure with scanner and report modules
- `bughunter-one` command-line interface
- TOML configuration support
- Structured console and file logging
- JSON payload and HTML, Markdown, PDF, and JSON report outputs

### Phase 2

- Target validation and URL normalization
- DNS A, AAAA, and CNAME lookup when available
- `robots.txt` and `sitemap.xml` collection
- HTTP header and cookie collection
- Header/content technology fingerprinting
- Report generation through the provider-agnostic report engine

### Phase 3

- Passive subdomain enumeration hints
- Optional live-host detection
- Passive port and service identification
- JavaScript asset collection
- Historical public URL collection
- Optional public directory discovery
- API endpoint discovery heuristics
- Authentication-surface detection

### Phase 4

- Local, read-only dashboard for an existing JSON payload
- TOML configuration system
- Structured logging with debug and file output options
- Retry support for text-resource requests
- Concurrent robots.txt and sitemap.xml retrieval
- Per-module output toggles that preserve payload keys
- Expanded documentation and regression tests
- Configurable timeout, user agent, rate limit, and active checks

### Phase 5

- Optional post-scan plugins discovered through Python entry points
- GitHub Actions verification on push and pull requests
- Docker image and Docker Compose scanner/dashboard services
- Release metadata, release notes, examples, and operational guides

## Installation

Clone and install the project in editable mode:

```bash
git clone https://github.com/bughunter9142-oss/bughunter-one.git
cd bughunter-one

python3 -m venv venv
source venv/bin/activate

python -m pip install -r requirements.txt
python -m pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.\venv\Scripts\Activate.ps1
```

The package provides `bughunter-one` and `bughunter-dashboard` console commands.

## CLI Usage

### Basic scan

```bash
bughunter-one https://example.com
```

### Write a payload and reports

```bash
bughunter-one https://example.com --output payload.json --reports-dir reports
```

`--output` accepts a JSON file path or a directory. `--reports-dir` writes `report.html`, `report.md`, `report.pdf`, and `report.json`.

### Use a configuration file

```bash
bughunter-one https://example.com --config bughunter.toml --output payload.json
```

When `--config` is used without `--reports-dir`, the configured `reports.output_dir` is used. Add `--debug` to emit debug-level structured logs.

### Start the dashboard

```bash
bughunter-dashboard payload.json
```

### Help

```bash
bughunter-one --help
bughunter-dashboard --help
```

## Dashboard

The dashboard does not scan targets. It loads an existing JSON payload and serves it at `http://127.0.0.1:8765` by default.

```bash
bughunter-dashboard payload.json --host 127.0.0.1 --port 8765
```

It displays the scan summary, DNS information, detected technologies, subdomains, live hosts, public ports/services, JavaScript assets, historical URLs, API endpoints, authentication pages, HTTP headers, cookies, and SSL information.

## Configuration

Copy [`bughunter.toml.example`](bughunter.toml.example) and adjust it as needed:

```toml
[scan]
timeout = 5
user_agent = "BugHunter-One/0.2.0"
concurrency = 2
active_checks = false
rate_limit = 0.2
retries = 1

[reports]
output_dir = "reports"

[logging]
level = "INFO"
file = "logs/bughunter-one.jsonl"

[modules]
dns = true
robots = true
sitemap = true
```

| Option | Meaning |
| --- | --- |
| `scan.timeout` | Request timeout in seconds. |
| `scan.user_agent` | User-Agent header used for scanner requests. |
| `scan.concurrency` | Worker limit for independent robots.txt and sitemap.xml retrieval. |
| `scan.active_checks` | Enables the existing optional active host/directory checks; default is `false`. |
| `scan.rate_limit` | Delay in seconds between active directory requests. |
| `scan.retries` | Additional attempts for robots.txt and sitemap.xml retrieval. |
| `reports.output_dir` | Default report directory when `--config` is used without `--reports-dir`. |
| `logging.level` | Console/file logging threshold, such as `INFO` or `DEBUG`. |
| `logging.file` | Optional JSON-lines log-file path. |
| `modules.<name>` | Enables or disables a scan section. Disabled sections remain present in the payload with empty results. |

Module names include `dns`, `robots`, `sitemap`, `headers`, `cookies`, `javascript`, `technologies`, `ssl`, `subdomains`, `live_hosts`, `public_ports`, `historical_urls`, `public_directories`, `api_discovery`, and `auth_surface`.

## Project Structure

```text
bughunter-one/
├── .github/workflows/ci.yml
├── bughunter.toml.example
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── README.md
├── RELEASE_NOTES.md
├── docker-compose.yml
├── examples/
│   ├── bughunter.toml
│   ├── payload.json
│   └── reports/report.md
├── pyproject.toml
├── requirements.txt
├── scripts/generate_example_reports.py
├── docs/
│   ├── CONFIGURATION.md
│   ├── DASHBOARD_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── FAQ.md
│   ├── INSTALLATION.md
│   ├── PLUGIN_DEVELOPMENT.md
│   ├── TROUBLESHOOTING.md
│   └── USER_GUIDE.md
├── src/
│   ├── ai_report_module/
│   │   ├── engine.py
│   │   └── providers/
│   │       ├── base.py
│   │       └── mock.py
│   └── bughunter_one/
│       ├── cli.py
│       ├── config.py
│       ├── dashboard.py
│       ├── engine.py
│       ├── logging_utils.py
│       └── plugins.py
└── tests/
    ├── test_cli.py
    ├── test_phase3_reconnaissance.py
    ├── test_phase4.py
    ├── test_plugins.py
    ├── test_reconnaissance_engine.py
    └── test_report_engine.py
```

## Reports

The report engine consumes the scanner payload and writes:

- **HTML**: browser-friendly report.
- **Markdown**: text-based report for review or version control.
- **PDF**: placeholder PDF output in the current implementation.
- **JSON**: structured report for downstream automation.

The raw scan payload includes target metadata, scan statistics, DNS, technologies, robots/sitemap entries, subdomains, host and port hints, JavaScript assets, historical URLs, directories, API and authentication findings, headers, cookies, SSL details, and metadata.

## Example Workflow

```bash
git clone https://github.com/bughunter9142-oss/bughunter-one.git
cd bughunter-one
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .

bughunter-one https://example.com --output payload.json --reports-dir reports
bughunter-dashboard payload.json
```

Open `http://127.0.0.1:8765` to view the payload. Reports are written to `reports/`.

## Testing

Run the complete test suite:

```bash
python -m pytest -q
```

If the default Windows pytest temporary directory is unavailable, use a workspace-local temporary directory:

```powershell
python -m pytest -q --basetemp .pytest-tmp
```

## Plugins

Plugins are optional post-scan payload enrichers. A plugin exposes a `name` and `apply(payload)` method, and is registered using the `bughunter_one.plugins` Python entry-point group. Enable or disable an installed plugin in TOML:

```toml
[plugins]
my-plugin = true
```

Plugin failures are isolated: the scan completes and records the error under `metadata.plugin_errors`.

## Docker

Build and run a sample scan, then serve its dashboard:

```bash
docker compose run --rm scanner
docker compose up dashboard
```

The scanner writes `/data/payload.json` and reports through the mounted `artifacts/` directory. See [docs/DASHBOARD_GUIDE.md](docs/DASHBOARD_GUIDE.md) for dashboard details.

## Roadmap

- Phase 1 ✅
- Phase 2 ✅
- Phase 3 ✅
- Phase 4 ✅
- Phase 5 ✅
- Phase 5 (Planned)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes focused, preserve the established payload schema and CLI behavior, add or update tests for behavior changes, update documentation, and run the full test suite before opening a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
