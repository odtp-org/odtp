from setuptools import setup, find_packages

setup(
    name='odtp',
    version='0.2.1',
    packages=find_packages(),
    description='Open Digital Twin Platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Carlos Vivar Rios',
    author_email='carlos.vivarrios@epfl.ch',
    url='https://github.com/odtp-org/odtp',
    install_requires=[
        # List of packages required by this module
        'pydantic==2.5.2',
        'typer==0.9.0',
        'pymongo==3.12.0'
    ],
    classifiers=[
        # Trove classifiers
        # Full list at https://pypi.org/classifiers/
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GLP 3 License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'odtp=odtp.cli:app',
        ],
    },
    python_requires='==3.11.5',
)