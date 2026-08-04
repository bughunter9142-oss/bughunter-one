# BugHunter One 0.3.0 Release Candidate

## Highlights

- Additive plugin architecture with entry-point discovery, registration, configuration toggles, and failure isolation.
- GitHub Actions CI across Windows, macOS, Linux, and supported Python versions.
- Docker image and Compose services for scanning and a local dashboard.
- Release metadata, examples, cross-platform checks, and expanded documentation.

## Compatibility

Phase 1–4 CLI behavior, payload schema, dashboard, reports, configuration, and tests remain supported. Plugins are optional post-scan enrichers and do not alter built-in scanner modules.
