---
description: Install dependencies for the web-factory gateway Worker
---
Install the Node.js dependencies for the web-factory Hono gateway Worker.

```bash
cd "${CLAUDE_PLUGIN_ROOT}/worker" && bun install
```

After installation, verify:

```bash
cd "${CLAUDE_PLUGIN_ROOT}/worker" && bunx wrangler --version
```
