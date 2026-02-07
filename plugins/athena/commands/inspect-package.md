---
description: Inspect the contents of a .athenabrief or .athena package
---
Inspect a `.athenabrief` or `.athena` package and display its contents.

$ARGUMENTS

The argument should be a file path to a `.athenabrief` or `.athena` file.

## Steps

1. **Validate argument:** Ensure a file path was provided and the file exists.

2. **Inspect package:**
   ```bash
   python3 -c "
   import json, zipfile, sys
   from pathlib import Path

   path = sys.argv[1]
   if not Path(path).exists():
       print(f'Error: File not found: {path}')
       sys.exit(1)

   try:
       with zipfile.ZipFile(path, 'r') as zf:
           infos = zf.infolist()
           total = sum(i.file_size for i in infos)
           compressed = sum(i.compress_size for i in infos)

           # Detect format
           names = [i.filename for i in infos]
           if 'brief.md' in names:
               fmt = 'athenabrief (export)'
           elif any(n.startswith('notes/') for n in names):
               fmt = 'athena (import)'
           else:
               fmt = 'unknown'

           print(f'Package: {path}')
           print(f'Format: {fmt}')
           print(f'Files: {len(infos)}')
           print(f'Uncompressed: {total:,} bytes')
           print(f'Compressed: {compressed:,} bytes')
           print()
           print('Contents:')
           for info in sorted(infos, key=lambda x: x.filename):
               if not info.filename.endswith('/'):
                   size = info.file_size
                   if size < 1024:
                       sz = f'{size} B'
                   elif size < 1024*1024:
                       sz = f'{size/1024:.1f} KB'
                   else:
                       sz = f'{size/(1024*1024):.1f} MB'
                   print(f'  {info.filename:<50} {sz:>10}')

           # Preview manifest
           if 'manifest.json' in names:
               print()
               print('Manifest preview:')
               manifest = json.loads(zf.read('manifest.json'))
               print(json.dumps(manifest, indent=2)[:2000])
   except zipfile.BadZipFile:
       print(f'Error: Not a valid ZIP file: {path}')
       sys.exit(1)
   " "$ARGUMENTS"
   ```

3. **Report** the package type, file count, and key contents.
