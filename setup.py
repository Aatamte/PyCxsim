from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='CAES',
    version="0.1",
    packages=find_packages(where='src'),
    install_requires=requirements,  # List of dependencies
    package_dir={'': 'src'},
    # other parameters...
)
