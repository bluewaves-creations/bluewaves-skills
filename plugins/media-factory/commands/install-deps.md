---
description: Install Python dependencies required by media-factory skills
---
Install the fal-client Python package needed for media-factory skills.

```bash
uv pip install fal-client
```

If `uv` is not available, fall back to pip:

```bash
pip install fal-client
```

After installation, verify:

```bash
python3 -c "import fal_client; print('fal-client installed successfully')"
```
