from setuptools import setup, find_packages

setup(
    name="PySheetsDB",
    version="0.3.6",
    packages=find_packages(),
    py_modules=["py_sheets_db"],
    install_requires=[
        'google-api-python-client',
        'python-dotenv',
        # ... any other dependencies ...
    ],
)
