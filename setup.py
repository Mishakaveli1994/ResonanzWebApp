from setuptools import setup, find_packages

setup(
    name='NeighborNet',
    version='0.1.0',
    author="Mihail Topuzov",
    description="WebApp for grouping people living at identical addresses",
    packages=find_packages(),
    install_requires=[
        "pandas~=2.1.4",
        "pandas-schema~=0.3.6",
        "polars~=0.19.19",
        "dask~=2023.12.0",
        "rapidfuzz~=3.5.2",
        "Flask~=3.0.0",
        "deep-translator~=1.11.4"
    ],
)
