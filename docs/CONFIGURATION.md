# Configuration guide

Use TOML configuration as shown in `bughunter.toml.example`. All options have safe defaults. `active_checks` remains false by default. A disabled module retains its corresponding output key so reports and integrations remain compatible.

`[plugins]` uses installed plugin names as keys. Set a name to `false` to skip it without uninstalling it. Plugins not named in this table are enabled when discovered.
