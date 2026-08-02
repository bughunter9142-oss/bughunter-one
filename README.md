# AI Report Generation Module

A lightweight Python package for transforming scanner reconnaissance data into professional security reports.

## Features

- Accepts structured scan data from a scanner or other reconnaissance workflow
- Produces HTML, Markdown, PDF, and JSON reports
- Keeps the AI component focused on report generation and explanation only
- Uses a provider abstraction so different AI backends can be added later
- Includes a mock provider for local development and testing

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

```python
from pathlib import Path
from ai_report_module import ReportConfig, ReportEngine

payload = {
    "target": {"host": "example.com"},
    "scan_statistics": {"hosts_discovered": 2, "ports_open": 3},
    "technologies": ["nginx", "linux"],
    "dns": {"records": ["A", "AAAA"]},
    "subdomains": ["www.example.com"],
    "live_hosts": ["example.com"],
    "open_ports": [{"port": 80, "service": "http"}],
    "robots": {"entries": ["/admin"]},
    "sitemap": {"entries": ["/sitemap.xml"]},
    "javascript": {"files": ["/app.js"]},
    "historical_urls": ["https://example.com/old"],
    "api_discovery": ["/api/v1"],
    "auth_surface": ["/login"],
    "parameters": [{"name": "id", "source": "query"}],
    "headers": {"server": "nginx"},
    "cookies": [{"name": "session"}],
    "ssl": {"tls_version": "1.3"},
    "interesting_resources": [{"url": "https://example.com/robots.txt"}],
    "metadata": {"scanner": "demo"},
}

engine = ReportEngine(ReportConfig(output_dir=Path("reports"), provider="mock"))
engine.write_reports(payload)
```

## Project structure

```text
ai-report-generation-module/
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── requirements.txt
├── .gitignore
├── src/
│   └── ai_report_module/
│       ├── __init__.py
│       ├── engine.py
│       └── providers/
│           ├── __init__.py
│           ├── base.py
│           └── mock.py
└── tests/
    └── test_report_engine.py
```

## Development

Run the tests with:

```bash
python -m pytest -q
```

