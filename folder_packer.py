import os
import sys
import time
from pathlib import Path

# Maximum file size to read into memory (1 MB) to prevent RAM overload & freeze
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  

# Default directories and files to ignore
DEFAULT_IGNORE_DIRS = {
    '.git', '.svn', '.hg', 'node_modules', 'venv', '.venv', 'env', '.env',
    '__pycache__', '.idea', '.vscode', 'dist', 'build', 'out', 'target',
    '.next', '.nuxt', 'coverage', '.pytest_cache', '.mypy_cache', 'bin', 'obj'
}

DEFAULT_IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock',
    'Pipfile.lock', 'Cargo.lock', '.DS_Store', 'Thumbs.db', 'folder_packer.py'
}

# Binary extensions to skip content
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
    '.zip', '.tar', '.gz', '.7z', '.rar',
    '.exe', '.dll', '.so', '.dylib', '.bin', '.iso',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.mp3', '.mp4', '.wav', '.avi', '.mov', '.flv',
    '.pyc', '.pyo', '.pyd', '.db', '.sqlite', '.sqlite3', '.woff', '.woff2', '.ttf', '.eot'
}

def is_binary_file(filepath: Path) -> bool:
    if filepath.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with open(filepath, 'tr', encoding='utf-8') as f:
            f.read(1024)
            return False
    except Exception:
        return True

def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

class ThrottledProgressBar:
    def __init__(self, total: int):
        self.total = total
        self.start_time = time.time()
        self.last_update_time = 0.0

    def update(self, current: int, current_file: str = "", force: bool = False):
        now = time.time()
        # Refresh progress bar at most once every 100ms (0.1s) to prevent Windows terminal freeze
        if not force and (now - self.last_update_time < 0.1) and current < self.total:
            return

        self.last_update_time = now
        bar_length = 25
        percent = float(current) / self.total if self.total > 0 else 1.0
        arrow = '=' * int(round(percent * bar_length) - 1) + '>' if 0 < percent < 1.0 else '=' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(arrow))
        
        elapsed = now - self.start_time
        rate = current / elapsed if elapsed > 0 else 0
        remaining = (self.total - current) / rate if rate > 0 else 0
        
        elapsed_str = format_time(elapsed)
        eta_str = format_time(remaining)

        display_file = (current_file[:20] + '...') if len(current_file) > 23 else current_file.ljust(23)

        sys.stdout.write(f"\r[{arrow}{spaces}] {percent*100:5.1f}% ({current}/{self.total}) | {elapsed_str} | ETA:{eta_str} | {display_file}")
        sys.stdout.flush()

def generate_tree(dir_path: Path, prefix: str = "") -> list:
    tree_lines = []
    try:
        entries = sorted(list(dir_path.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
    except Exception:
        return [f"{prefix}└── [Permission Denied or Error]"]

    entries = [
        e for e in entries 
        if e.name not in DEFAULT_IGNORE_DIRS and e.name not in DEFAULT_IGNORE_FILES and not e.name.startswith('.')
    ]

    count = len(entries)
    for i, entry in enumerate(entries):
        is_last = (i == count - 1)
        connector = "└── " if is_last else "├── "
        tree_lines.append(f"{prefix}{connector}{entry.name}")
        
        if entry.is_dir():
            extension = "    " if is_last else "│   "
            tree_lines.extend(generate_tree(entry, prefix + extension))
            
    return tree_lines

def pack_folder(folder_path: str, output_file: str = None):
    target_dir = Path(folder_path).resolve()
    
    if not target_dir.exists():
        print(f"[ERROR] Folder '{folder_path}' does not exist.")
        return
    if not target_dir.is_dir():
        print(f"[ERROR] '{folder_path}' is not a directory.")
        return

    if not output_file:
        output_file = target_dir.parent / f"{target_dir.name}_context.md"
    else:
        output_file = Path(output_file).resolve()

    print(f"[INFO] Scanning directory: {target_dir}")
    
    # Safely collect files
    file_tasks = []
    for root, dirs, files in os.walk(target_dir):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_DIRS and not d.startswith('.')]
        dirs.sort()
        files.sort()
        for file in files:
            if file in DEFAULT_IGNORE_FILES or file.startswith('.'):
                continue
            filepath = Path(root) / file
            # Ignore output file itself if inside target dir
            if filepath.resolve() == output_file.resolve():
                continue
            rel_path = filepath.relative_to(target_dir)
            file_tasks.append((rel_path, filepath))

    total_files = len(file_tasks)
    if total_files == 0:
        print("[WARNING] No eligible files found to process.")
        return

    print(f"[INFO] Found {total_files} files. Building folder tree...")
    
    output_path = Path(output_file)

    # Stream directly to file to prevent RAM freeze and high memory consumption
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write(f"# Project Structure & Contents: `{target_dir.name}`\n\n")
        out_f.write("## Folder Tree\n\n```\n")
        out_f.write(f"{target_dir.name}/\n")
        tree_lines = generate_tree(target_dir)
        out_f.write("\n".join(tree_lines))
        out_f.write("\n```\n\n---\n\n")
        out_f.write("## File Contents\n\n")

        print(f"[INFO] Processing files safely...")
        progress = ThrottledProgressBar(total_files)
        start_time = time.time()
        
        processed_count = 0
        skipped_count = 0

        for rel_path, filepath in file_tasks:
            processed_count += 1
            progress.update(processed_count, str(rel_path))

            # File size safety check
            try:
                file_size = filepath.stat().st_size
            except Exception:
                file_size = 0

            if file_size > MAX_FILE_SIZE_BYTES:
                skipped_count += 1
                size_mb = file_size / (1024 * 1024)
                out_f.write(f"### File: `{rel_path}`\n\n*(File omitted: Too large - {size_mb:.2f} MB)*\n\n---\n\n")
                continue

            if is_binary_file(filepath):
                skipped_count += 1
                out_f.write(f"### File: `{rel_path}`\n\n*(Binary or non-text file content omitted)*\n\n---\n\n")
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                ext = filepath.suffix.lstrip('.')
                lang = ext if ext else ""

                out_f.write(f"### File: `{rel_path}`\n\n```{lang}\n{content}\n```\n\n---\n\n")
            except Exception as e:
                skipped_count += 1
                out_f.write(f"### File: `{rel_path}`\n\n*(Could not read file content: {e})*\n\n---\n\n")

        progress.update(total_files, "Done", force=True)
        print()

    total_time = time.time() - start_time
    print("[SUCCESS] Processing completed successfully!")
    print(f"-> Total Time: {format_time(total_time)} ({total_time:.2f} seconds)")
    print(f"-> Files processed: {total_files - skipped_count}")
    print(f"-> Files skipped (large/binary/ignored): {skipped_count}")
    print(f"-> Output saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Enter folder name or path: ").strip()

    if target:
        target = target.strip('"\'')
        pack_folder(target)
    else:
        print("[ERROR] No folder specified.")
