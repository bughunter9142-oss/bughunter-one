# FAQ

## Does BugHunter One exploit targets?

No. It is designed for passive, informational reconnaissance. Optional active checks remain disabled by default.

## Does the dashboard scan a target?

No. It renders an existing payload only.

## How do I disable a plugin?

Set its name to `false` under `[plugins]` in the TOML configuration.

## Is the PDF report production-rendered?

No. The current report engine writes a placeholder PDF stub; HTML, Markdown, and JSON contain the generated report content.
