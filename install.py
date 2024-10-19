#!/usr/bin/env python3
from pathlib import Path
import os

if os.path.exists('boundaries.py'):
    if os.path.islink('boundaries.py'):
        os.unlink('boundaries.py')
    else:
        os.remove('boundaries.py')

Path('boundaries.py').symlink_to('../apps/boundaries/main.py')

os.chmod("bpb.py", 744)