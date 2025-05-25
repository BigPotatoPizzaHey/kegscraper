from setuptools import setup
import os

with open("README.md", 'r') as rmf:
    longdesc = rmf.read()

with open("LICENSE", "r") as lf:
    lisc = lf.read()

setup(
    name='kegscraper',
    version='v0.1.7',
    packages=['kegscraper'] + [f"kegscraper.{subdir}" for subdir in next(os.walk("kegscraper"))[1] if subdir != "__pycache__"],
    url='https://kegs.org.uk/',
    license=lisc,
    author='BigPotatoPizzaHey',
    author_email="poo@gmail.com",
    description="The ultimate KEGS webscraping module",
    long_description=longdesc,
    long_description_content_type="text/markdown",
)
