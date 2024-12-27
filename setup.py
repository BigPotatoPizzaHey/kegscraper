from setuptools import setup

with open("README.md", 'r') as rmf:
    longdesc = rmf.read()

setup(
    name='kegscraper',
    version='v0.1.2',
    packages=['kegscraper'],
    url='https://github.com/BigPotatoPizzaHey/kegscraper/',
    license='unlicense',
    author='BigPotatoPizzaHey',
    author_email="poo@gmail.com",
    description="The ultimate KEGS webscraping module",
    long_description=longdesc
)
