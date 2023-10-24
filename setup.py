from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='pycxsim',
    version="0.1.4",
    license="MIT",
    author="Aaron Tamte",
    author_email="aaron2804@gmail.com",
    packages=find_packages(where='src'),
    python_requires='>=3.8',
    install_requires=requirements,  # List of dependencies
    description="PyCxsim is a framework to simulate computational agents in a confined environment.",
    url="https://github.com/Aatamte/PyCxsim",
    keywords=["Artificial Intelligence", "Simulation"],
    package_dir={'': 'src'},
    package_data={
        'cxsim': ['prompts/*.txt', 'gui/assets/*.ico'],
    },
    # other parameters...
)
