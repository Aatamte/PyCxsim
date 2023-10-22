import os


def print_directory_structure(start_directory):
    for root, dirs, files in os.walk(start_directory):
        # Skip the .git directory
        if '.git' in dirs:
            dirs.remove('.git')

        level = root.replace(start_directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{sub_indent}{f}')


if __name__ == "__main__":
    project_root_dir = os.getcwd()  # Gets the current working directory
    print_directory_structure(project_root_dir)