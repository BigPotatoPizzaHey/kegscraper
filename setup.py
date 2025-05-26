from setuptools import setup
import os

requires = [
    "requests~=2.32.3",
    "bs4~=0.0.2",
    "beautifulsoup4~=4.12.3",
    "dateparser~=1.2.0",
    "setuptools~=75.6.0",
    "pypdf~=5.1.0",
    "pyperclip~=1.9.0"
]

setup(
    name='kegscraper',
    version='v0.1.11',
    packages=['kegscraper'] +
             [f"kegscraper.{subdir}" for subdir in next(os.walk("kegscraper"))[1] if subdir != "__pycache__"],
    project_urls={
        "Homepage": 'https://kegs.org.uk/',
        "Source": "https://github.com/BigPotatoPizzaHey/kegscraper",
        "Documentation": "https://github.com/BigPotatoPizzaHey/kegscraper/wiki"
    },
    license=open("LICENSE").read(),
    author='BigPotatoPizzaHey',
    author_email="poo@gmail.com",
    description="The ultimate KEGS webscraping module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=requires,
    data_files=[("/", ["requirements.txt"])]
)
