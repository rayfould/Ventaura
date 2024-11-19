import subprocess

# Define file extensions to include (adjust as needed)
valid_extensions = (".py", ".js", ".cs", ".html", ".css", ".ts")

# Run git command to list files
files = subprocess.check_output("git ls-files", shell=True).decode().splitlines()

total_lines = 0

for file in files:
    # Skip files in the venv folder and non-source files
    if "venv" in file or not file.endswith(valid_extensions):
        continue

    try:
        with open(file, 'r', encoding='utf-8') as f:
            # Count non-empty lines that are not import statements
            total_lines += sum(
                1 for line in f
                if line.strip() and not (line.strip().startswith("import") or line.strip().startswith("from"))
            )
    except Exception as e:
        print(f"Error reading {file}: {e}")

print(f"Total lines of code (excluding empty lines, imports, and venv): {total_lines}")
