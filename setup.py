from setuptools import setup
import json

with open('config.json') as f:
    setup_args = json.load(f)

setup(**setup_args)
