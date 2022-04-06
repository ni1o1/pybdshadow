import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pybdshadow",
    version="0.1.1",
    author="Qing Yu",
    author_email="qingyu0815@foxmail.com",
    description="Python package to generate building shadow geometry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    url="https://github.com/ni1o1/pybdshadow",
    project_urls={
        "Bug Tracker": "https://github.com/ni1o1/pybdshadow/issues",
    },
    install_requires=[
        "numpy", "pandas", "shapely", "geopandas", "matplotlib","suncalc"
    ],
    classifiers=[
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    package_dir={'pybdshadow': 'src/pybdshadow'},
    packages=['pybdshadow'],
    python_requires=">=3.6",
)
