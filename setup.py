from setuptools import setup

# The text of the README file
README = open("README.md").read()

# This call to setup() does all the work
setup(
    name="csv-merge",
    version="0.1.0",
    description="""
      Command line tools to merge the most recent version of several CSV files
      containing data on the same users, into one up-to-date CSV file, according
      to a YAML configuration file.
      """,
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jlumbroso/csv-merge",
    author="Jérémie Lumbroso",
    author_email="lumbroso@cs.princeton.edu",
    license="LGPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[],
    scripts=["src/csv-merge"],
    install_requires=[
        "PyYAML",
        "simpleeval"
    ],
    include_package_data=True,
)
