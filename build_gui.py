import os
import subprocess
import shutil

# Define the absolute paths
project_root = os.path.abspath(os.path.dirname(__file__))
gui_directory = os.path.join(project_root, 'gui')
build_directory = os.path.join(gui_directory, 'build')
destination_directory = os.path.join(project_root, 'src', 'cxsim', 'experimental', 'gui', 'build')

# Path to npm
npm_path = r'C:\Program Files\nodejs\npm.cmd'

# Run the build command in the GUI directory
subprocess.run([npm_path, 'run', 'build'], cwd=gui_directory, check=True)

# Check if the build directory exists and move the files
if os.path.exists(build_directory):
    # If the destination directory doesn't exist, create it
    os.makedirs(destination_directory, exist_ok=True)

    # Move the build files to the destination directory
    for item in os.listdir(build_directory):
        source_item = os.path.join(build_directory, item)
        destination_item = os.path.join(destination_directory, item)

        if os.path.exists(destination_item):
            if os.path.isdir(destination_item):
                shutil.rmtree(destination_item)
            else:
                os.unlink(destination_item)

        shutil.move(source_item, destination_item)
    print(f'Build files have been moved to {destination_directory}')
else:
    print('Build directory does not exist. Build process might have failed.')
