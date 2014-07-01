from setuptools import find_packages, setup

setup(
    name='supernode',
    version='1.0.6',
    description='Python command-line client for creating and managing super node packages',
    install_requires=[
        'boto == 2.29.1',
        'docopt == 0.6.1',
        'futures == 2.1.6',
        'progressbar2 == 2.6.2',
        'requests >= 2.0'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'supernode = supernode.cli:main'
        ]
    }
)