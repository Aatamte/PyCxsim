import os

def print_directory_structure(directory, level=0):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        indent = '    ' * level
        if os.path.isdir(item_path):
            print(f"{indent}[{item}]")
            print_directory_structure(item_path, level + 1)
        else:
            print(f"{indent}{item}")

# Get the current directory
current_directory = os.getcwd()

print(f"Directory structure for: {current_directory}")
print_directory_structure(current_directory)