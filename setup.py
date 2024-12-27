from setuptools import setup

with open("README.md", 'r') as rmf:
    longdesc = rmf.read()

setup(
    name='kegscraper',
    version='v0.1.3',
    packages=['kegscraper'],
    url='https://kegs.org.uk/',
    license='unlicense',
    author='BigPotatoPizzaHey',
    author_email="poo@gmail.com",
    description="The ultimate KEGS webscraping module",
    long_description=longdesc,
    long_description_content_type="text/markdown"
)
