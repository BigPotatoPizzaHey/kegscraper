from setuptools import setup
import os

setup(
    name='kegscraper',
    version='v0.1.9',
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
        "requests~=2.32.3",
        "bs4~=0.0.2",
        "beautifulsoup4~=4.12.3",
        "dateparser~=1.2.0",
        "setuptools~=75.6.0",
        "pypdf~=5.1.0",
        "pyperclip~=1.9.0"
    ]
)
