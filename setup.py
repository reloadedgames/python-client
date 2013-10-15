from setuptools import find_packages, setup

setup(
    name='supernode',
    version='1.0',
    description='Python command-line client for creating and managing super node packages',
    install_requires=[
        'docopt == 0.6.1',
        'paramiko >= 1.12.0',
        'requests >= 2.0'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'supernode = supernode.cli:main'
        ]
    }
)