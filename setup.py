from setuptools import find_packages, setup

setup(
    name='supernode',
    version='1.0.5.2',
    description='Python command-line client for creating and managing super node packages',
    install_requires=[
        'boto == 2.29.1',
        'docopt == 0.6.1',
        'gevent == 1.0.1',
        'requests >= 2.0'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'supernode = supernode.cli:main'
        ]
    }
)