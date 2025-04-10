from setuptools import setup, find_packages

setup(
    name="eClass-Scraper",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4"
    ],
    entry_points={
        "console_scripts": [
            "ecs=ecs.cli:main"
        ]
    },
)
