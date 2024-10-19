#!/usr/bin/env python3
from pathlib import Path
import os

if os.path.exists('boundaries.py'):
    if os.path.islink('boundaries.py'):
        os.unlink('boundaries.py')
    else:
        os.remove('boundaries.py')

Path('boundaries.py').symlink_to('../boundaries/main.py')

os.system("chmod u+x bpb.py")