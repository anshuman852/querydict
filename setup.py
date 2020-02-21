import setuptools
from lucene_dict_matcher import VERSION_STRING

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lucene-dict-matcher",
    version=VERSION_STRING,
    author="David Cannings",
    author_email="david@edeca.net",
    description="Match Python dictionaries using Lucene queries",
    license="GNU Affero General Public License v3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edeca/lucene-dict-matcher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Environment :: Win32 (MS Windows)",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    install_requires=["luqum", "dotty_dict",],
    test_suite='nose.collector',
    tests_require=['nose', 'pytest'],
)
