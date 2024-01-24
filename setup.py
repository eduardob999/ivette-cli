from setuptools import setup

setup(
    name='ivette-client',
    version='0.1.0',
    description='Python client for Ivette Computational chemistry and Bioinformatics project',
    author='Eduardo Bogado',
    py_modules=['run_ivette',
                'ivette',
                'ivette.classes',
                'ivette.decorators',
                'ivette.newtworking', 'ivette'],
    entry_points={
        'console_scripts': [
            'ivette=run_ivette:main',
        ],
    },
)
