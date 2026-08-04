# Developer guide

Scanner changes belong in `src/bughunter_one`; reporting remains in `src/ai_report_module`. Preserve the established payload keys and run `python -m pytest -q --basetemp .pytest-tmp` on Windows environments where the default pytest temp directory is unavailable.
