from setuptools import setup
import os

setup(
    name='kegscraper',
    version='v0.1.10',
    packages=['kegscraper'] +
             [f"kegscraper.{subdir}" for subdir in next(os.walk("kegscraper"))[1] if subdir != "__pycache__"],
    url='https://kegs.org.uk/',
    license=open("LICENSE").read(),
    author='BigPotatoPizzaHey',
    author_email="poo@gmail.com",
    description="The ultimate KEGS webscraping module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    requires=[
        'requests',
        'bs4',
        'beautifulsoup4',
        'dateparser',
        'setuptools',
        'pypdf',
        'pyperclip'
    ],
    data_files=[("/", ["requirements.txt"])]
)
