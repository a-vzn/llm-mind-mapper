import shutil
import os
from pathlib import Path

def clean():
    """Clean all cache and temporary files."""
    patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        'build',
        'dist',
        '*.egg-info',
        'output'
    ]
    
    for pattern in patterns:
        if os.path.isdir(pattern):
            shutil.rmtree(pattern, ignore_errors=True)
        else:
            for path in Path('.').rglob(pattern):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
    
    print("Cleanup completed!")

if __name__ == "__main__":
    clean()