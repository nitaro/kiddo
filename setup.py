from setuptools import setup, setuptools
from kiddo import __NAME__, __DESCRIPTION__, __AUTHOR__, __URL__, __VERSION__

doc = "README.md"
def read_doc():
    with open(doc) as d:
        return d.read()
		
setup(
    name = __NAME__,
    description = __DESCRIPTION__,
    author = __AUTHOR__,
    doc = __DESCRIPTION__,
    url = __URL__,
    version = __VERSION__,
    packages = setuptools.find_packages(),
    include_package_data = True,
    python_requires = ">=3.5",
    license = "LICENSE.txt",
    long_description = read_doc(),
)
