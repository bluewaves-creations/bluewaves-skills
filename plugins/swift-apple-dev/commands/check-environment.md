---
description: Audit Xcode, Swift, SDKs, and simulators for swift-apple-dev readiness
---
Run a comprehensive environment check for Apple Swift development readiness.

## Checks

1. **Xcode version** (requires 26+):
   ```bash
   xcodebuild -version
   ```

2. **Swift version** (requires 6+):
   ```bash
   swift --version
   ```

3. **Active developer directory:**
   ```bash
   xcode-select -p
   ```

4. **Available SDKs:**
   ```bash
   xcodebuild -showsdks
   ```

5. **Available simulators:**
   ```bash
   xcrun simctl list devices available --json | python3 -c "
   import sys, json
   data = json.load(sys.stdin)
   for runtime, devices in data.get('devices', {}).items():
       running = [d for d in devices if d.get('state') == 'Booted']
       available = [d for d in devices if d.get('isAvailable', False)]
       if available:
           name = runtime.split('.')[-1] if '.' in runtime else runtime
           print(f'  {name}: {len(available)} devices ({len(running)} booted)')
   "
   ```

6. **Summary:** Report whether the environment meets swift-apple-dev requirements (Xcode 26+, Swift 6+) with clear pass/fail for each check and actionable next steps for any failures.
