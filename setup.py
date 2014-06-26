from setuptools import find_packages, setup

setup(
    name='supernode',
    version='1.0.5.2',
    description='Python command-line client for creating and managing super node packages',
    install_requires=[
        'docopt == 0.6.1',
        'requests >= 2.0',
        'progressbar2 == 2.6.2'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'supernode = supernode.cli:main'
        ]
    }
)