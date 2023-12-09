import os


def list_directories(startpath):
    for root, dirs, files in os.walk(startpath, topdown=True):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__']]

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f'{indent}{os.path.basename(root)}/')

        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith('.py'):
                print(f'{subindent}{f}')


if __name__ == "__main__":
    current_directory = os.getcwd()
    print(f"Current Directory Structure of: {current_directory}")
    list_directories(current_directory)




