# BugHunter One

BugHunter One is a lightweight reconnaissance and report-generation toolkit for turning target discovery data into structured security-report artifacts. The current implementation includes a CLI-based scanner that collects basic reconnaissance information and a report engine that converts that payload into HTML, Markdown, PDF, and JSON outputs.

## Project overview

The repository currently contains two cooperating components:

- The BugHunter One scanner package, implemented under src/bughunter_one, which validates a target, performs basic HTTP and DNS reconnaissance, and produces a structured JSON payload.
- The AI report module, implemented under src/ai_report_module, which builds a report from that payload and writes output files for downstream use.

The current implementation is intentionally lightweight and uses a mock provider for report generation. It is designed as a starting point for future integration with additional AI backends.

## Features

- CLI-based reconnaissance scanning for a target URL or hostname
- Target validation and normalization before scanning
- DNS resolution for common record types when dnspython is available
- Fetching of robots.txt and sitemap.xml resources when reachable
- HTTP request inspection for headers, cookies, and JavaScript file references
- Simple technology fingerprinting from response headers and page content
- SSL status inference for HTTP and HTTPS targets
- Structured payload generation with sections for scan statistics, DNS, technologies, subdomains, ports, robots data, sitemap data, and metadata
- Report generation in HTML, Markdown, PDF, and JSON formats
- Provider abstraction for future AI backends, with a built-in mock provider

## Installation

From the repository root, install the runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

To install the package in editable mode:

```bash
python -m pip install -e .
```

## Requirements

- Python 3.10 or newer
- requests
- dnspython (recommended; if unavailable, DNS resolution falls back to an empty result)
- pytest (for running tests)

## CLI usage

The package exposes the console script `bughunter-one`:

```bash
bughunter-one https://example.com --output payload.json --reports-dir reports
```

Arguments:

- `target`: required positional argument containing the target URL or hostname
- `--output`: optional path to save the generated JSON payload
- `--reports-dir`: optional directory where HTML, Markdown, PDF, and JSON report files will be written

The CLI prints the reconnaissance payload as JSON to stdout and optionally writes the payload and reports to disk.

## Scanner workflow

The scanner workflow is implemented in `src/bughunter_one/engine.py` and follows this sequence:

1. Validate and normalize the target input.
2. Build an initial payload with target metadata and baseline scan statistics.
3. Perform DNS resolution for the target host when possible.
4. Fetch `robots.txt` and `sitemap.xml` resources if available.
5. Request the target URL and inspect response headers, cookies, and JavaScript references.
6. Fingerprint visible technologies from headers and page content.
7. Infer basic SSL details based on the scheme.
8. Return a structured payload suitable for report generation.

## Report generation workflow

The report workflow is implemented in `src/ai_report_module/engine.py`.

Example:

```python
from pathlib import Path
from ai_report_module import ReportConfig, ReportEngine
from bughunter_one.engine import ReconnaissanceEngine

scanner = ReconnaissanceEngine()
payload = scanner.scan_target("https://example.com")

engine = ReportEngine(ReportConfig(output_dir=Path("reports"), provider="mock"))
engine.write_reports(payload)
```

The `generate()` method returns a structured report dictionary. The `write_reports()` method writes:

- `report.html`
- `report.md`
- `report.pdf`
- `report.json`

The current implementation uses a mock provider for the AI-generated summary text and writes a placeholder PDF stub rather than rendering a true PDF document.

## Project architecture

The core modules are:

- `src/bughunter_one/cli.py`: CLI entry point for running the scanner and generating optional reports
- `src/bughunter_one/engine.py`: reconnaissance engine and payload-building logic
- `src/ai_report_module/engine.py`: report engine for structured report generation
- `src/ai_report_module/providers/base.py`: abstract AI provider interface
- `src/ai_report_module/providers/mock.py`: mock implementation used by the current default flow

## Directory structure

```text
ai-report-generation-module/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── payload.json
├── pyproject.toml
├── README.md
├── requirements.txt
├── reports/
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
    └── test_report_engine.py
```

## Examples

### Example CLI run

```bash
bughunter-one https://example.com --output payload.json --reports-dir reports
```

This writes a JSON payload to `payload.json` and report artifacts to `reports/`.

### Example Python usage

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

## Output formats

The scanner produces a JSON payload with the following high-level structure:

- `target`: normalized target host and URL
- `scan_statistics`: discovered hosts, open ports, scan timestamps
- `technologies`: list of detected technologies
- `dns`: DNS records gathered for the target
- `subdomains`: discovered subdomains (currently empty in the default implementation)
- `live_hosts`: list of reachable hosts
- `open_ports`: discovered open port records
- `robots`: robots.txt data and parsed entries
- `sitemap`: sitemap data and parsed entries
- `javascript`: discovered JavaScript asset references
- `headers`, `cookies`, `ssl`: HTTP response details
- `interesting_resources`: notable resources discovered during scanning
- `metadata`: scanner metadata and target details

The report engine writes the same content into:

- HTML for browser-friendly report rendering
- Markdown for text-based output
- PDF as a placeholder file in the current implementation
- JSON for machine-readable storage and downstream processing

## Development instructions

To work on the project locally:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

The package is intentionally simple and can be extended by adding new providers under `src/ai_report_module/providers/` or by expanding the scanner logic in `src/bughunter_one/engine.py`.

## Testing instructions

Run the test suite with:

```bash
python -m pytest -q
```

The current tests verify that the report engine builds structured content and writes HTML, Markdown, PDF, and JSON outputs successfully.

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

