import os


def count_lines_in_file(file_path):
    """Count non-blank lines in a single file."""
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  # Skip blank lines
                    count += 1
    except UnicodeDecodeError:
        # Fall back to a more permissive encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                for line in file:
                    if line.strip():  # Skip blank lines
                        count += 1
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return count


def count_lines_in_repo(repo_path, extensions=None, excluded_dirs=None):
    """
    Count non-blank lines of code in a repository.

    Args:
        repo_path (str): Path to the repository.
        extensions (list): List of file extensions to include (e.g., ['.py', '.js']).
                           If None, all files are included.
        excluded_dirs (list): List of directory names to exclude.

    Returns:
        int: Total number of non-blank lines of code.
    """
    total_lines = 0
    for root, dirs, files in os.walk(repo_path):
        # Exclude specific directories
        dirs[:] = [d for d in dirs if d not in (excluded_dirs or [])]

        for file in files:
            if extensions is None or any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                total_lines += count_lines_in_file(file_path)
    return total_lines


if __name__ == "__main__":
    # Set the path to your repository
    repo_path = input("Enter the path to your repository: ").strip()

    # Specify file extensions to include, or set to None to include all files
    extensions = ['.py', '.js', '.java', '.cs', '.html', '.css']  # Add extensions as needed

    # Specify directories to exclude
    excluded_dirs = ['.venv', 'lib', 'site-packages', 'imports']
    excluded_files = ['.csv']


    print(f"Counting non-blank lines of code in repository: {repo_path}...")
    total_lines = count_lines_in_repo(repo_path, extensions, excluded_dirs)
    print(f"Total non-blank lines of code: {total_lines}")
