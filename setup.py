from setuptools import setup, find_packages

setup(
    name="PySheetsDB",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'google-api-python-client',
        # ... any other dependencies ...
    ],
)
