# Plugin development guide

Plugins are optional post-scan enrichers. They must provide a non-empty `name` and an `apply(payload)` method. The method receives the completed JSON-compatible payload and may add information in place.

Register a plugin in your package metadata:

```toml
[project.entry-points."bughunter_one.plugins"]
my-plugin = "my_package.plugin:MyPlugin"
```

Use the plugin name in `[plugins]` of BugHunter One configuration to enable or disable it. Plugin exceptions are logged and recorded in `metadata.plugin_errors`; they do not abort a completed scan.
