# BugHunter One

BugHunter One is a lightweight, passive reconnaissance toolkit that collects publicly available information about a target, builds a structured JSON payload, and generates human-readable reports in HTML, Markdown, PDF, and JSON formats. The current implementation covers Phases 1, 2, and 3 and is designed to preserve existing behavior while adding new passive recon capabilities.

## Project overview

BugHunter One is composed of two cooperating components:

- The scanner package in [src/bughunter_one](src/bughunter_one), which validates a target, performs passive reconnaissance, and builds a JSON payload.
- The report package in [src/ai_report_module](src/ai_report_module), which turns the scanner payload into HTML, Markdown, PDF, and JSON reports.

The project is intentionally passive and informational. It does not perform exploitation, brute force, authentication bypass, or invasive testing.

## Features implemented

### Phase 1
- CLI-based target scanning
- Project installation support via editable packaging
- Structured payload generation
- Report engine for HTML, Markdown, PDF, and JSON outputs
- Mock provider support for report summaries

### Phase 2
- Target validation and normalization
- DNS lookup for A/AAAA records when available
- robots.txt parsing
- sitemap.xml parsing
- HTTP header collection
- Cookie inspection
- Technology fingerprinting from headers and page content
- SSL status reporting for HTTP and HTTPS targets
- JSON payload enrichment with standard reconnaissance sections

### Phase 3
- Passive subdomain enumeration hints
- Live host detection for the target and discovered hosts
- Public port and service identification from passive data
- JavaScript asset collection
- Historical public URL collection
- Public directory discovery support
- API endpoint discovery heuristics
- Authentication surface detection
- Additional report sections for the new passive findings

## Requirements

- Python 3.10 or newer
- requests
- dnspython
- pytest

## Installation

Install runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

## CLI usage

The console entry point is `bughunter-one`.

```bash
bughunter-one https://example.com --output payload.json --reports-dir reports
```

Arguments:
- `target`: required target URL or hostname
- `--output`: optional path for the JSON payload
- `--reports-dir`: optional directory for generated reports

The CLI prints the JSON payload to stdout and writes the payload and reports to disk when the optional arguments are supplied.

## Python API usage

```python
from pathlib import Path
from ai_report_module import ReportConfig, ReportEngine
from bughunter_one.engine import ReconnaissanceEngine

scanner = ReconnaissanceEngine(timeout=10)
payload = scanner.scan_target("https://example.com")

config = ReportConfig(output_dir=Path("reports"), provider="mock")
engine = ReportEngine(config)
engine.write_reports(payload)
```

## Scanner workflow

The scanner flow in [src/bughunter_one/engine.py](src/bughunter_one/engine.py) follows this order:

1. Validate and normalize the target input.
2. Create a baseline payload with target metadata and scan statistics.
3. Resolve DNS records when possible.
4. Fetch and parse robots.txt and sitemap.xml.
5. Request the target URL and inspect headers, cookies, and page content.
6. Fingerprint visible technologies.
7. Infer basic SSL details.
8. Collect passive subdomain, host, port, JavaScript, and historical URL hints.
9. Discover likely public directories, API endpoints, and authentication surfaces.
10. Return a structured payload ready for reporting.

## Report generation workflow

The report engine in [src/ai_report_module/engine.py](src/ai_report_module/engine.py) builds a structured report from the scanner payload and writes the output files:

- HTML report
- Markdown report
- PDF report
- JSON report

Example:

```python
from pathlib import Path
from ai_report_module import ReportConfig, ReportEngine
from bughunter_one.engine import ReconnaissanceEngine

payload = ReconnaissanceEngine().scan_target("https://example.com")
engine = ReportEngine(ReportConfig(output_dir=Path("reports"), provider="mock"))
engine.write_reports(payload)
```

The current implementation uses a mock provider for the summary text and writes a placeholder PDF stub rather than a fully rendered PDF document.

## Project architecture

Key modules:
- [src/bughunter_one/cli.py](src/bughunter_one/cli.py): CLI entry point
- [src/bughunter_one/engine.py](src/bughunter_one/engine.py): reconnaissance engine and payload logic
- [src/ai_report_module/engine.py](src/ai_report_module/engine.py): report generation engine
- [src/ai_report_module/providers/base.py](src/ai_report_module/providers/base.py): provider abstraction
- [src/ai_report_module/providers/mock.py](src/ai_report_module/providers/mock.py): default mock provider

## Directory structure

```text
ai-report-generation-module/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
├── src/
│   ├── ai_report_module/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── mock.py
│   └── bughunter_one/
│       ├── __init__.py
│       ├── cli.py
│       └── engine.py
└── tests/
    ├── test_cli.py
    ├── test_phase3_reconnaissance.py
    └── test_report_engine.py
```

## Output formats

The scanner produces a JSON payload containing sections such as:
- `target`
- `scan_statistics`
- `technologies`
- `dns`
- `subdomains`
- `live_hosts`
- `open_ports`
- `robots`
- `sitemap`
- `javascript`
- `historical_urls`
- `api_discovery`
- `auth_surface`
- `public_ports`
- `public_directories`
- `headers`
- `cookies`
- `ssl`
- `interesting_resources`
- `metadata`

The report engine writes the same information into:
- HTML for browser-friendly presentation
- Markdown for text-based output
- PDF as a placeholder output in the current implementation
- JSON for structured downstream use

## Example commands

### CLI scan

```bash
bughunter-one https://example.com --output payload.json --reports-dir reports
```

### Python scan and report generation

```python
from pathlib import Path
from ai_report_module import ReportConfig, ReportEngine
from bughunter_one.engine import ReconnaissanceEngine

payload = ReconnaissanceEngine().scan_target("https://example.com")
engine = ReportEngine(ReportConfig(output_dir=Path("reports"), provider="mock"))
engine.write_reports(payload)
```

## Testing instructions

Run the full test suite:

```bash
python -m pytest -q
```

The current tests cover the CLI flow, the Phase 3 reconnaissance modules, and report generation.

## Development instructions

To work on the project locally:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

Extend the project by updating the scanner logic in [src/bughunter_one/engine.py](src/bughunter_one/engine.py) or by adding new providers under [src/ai_report_module/providers](src/ai_report_module/providers).

## Changelog summary

### Latest phase: Phase 3
- Added passive reconnaissance modules for subdomain hints, live host detection, public port/service identification, JavaScript collection, historical public URL collection, public directory discovery, API endpoint discovery, and authentication surface detection.
- Extended the report engine to include new sections for the new passive findings.
- Added regression and integration tests to preserve earlier behavior while expanding capabilities.
- Verified the project remains installable, runnable, and testable from a fresh environment.

