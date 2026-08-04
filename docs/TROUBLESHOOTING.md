# Troubleshooting guide

If console commands are unavailable, activate the virtual environment and reinstall with `python -m pip install -e .`. If pytest cannot create its Windows temp directory, run `python -m pytest -q --basetemp .pytest-tmp`.

The dashboard requires a JSON object payload. Docker dashboard startup requires `artifacts/payload.json`; run the scanner Compose service first. Plugin load failures are logged and plugin execution failures appear in `metadata.plugin_errors` without aborting the scan.
