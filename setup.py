from setuptools import find_packages, setup


def readme(path: str = "./README.md"):
    with open(path) as f:
        return f.read()


setup(
    name="studosi",
    version="0.0.0.dev2",
    description="The official Studoši Python toolkit",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/studosi/studosi-py",
    author="Miljenko Šuflaj [micho]",
    author_email="headsouldev@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Framework :: Flake8",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: Croatian",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Installation/Setup",
    ],
    keywords="studosi studoši toolkit development",
    project_urls={
        "Source": "https://github.com/studosi/studosi-py",
        "Issues": "https://github.com/studosi/studosi-py/issues",
    },
    packages=find_packages(
        include=(
            "studosi",
            "studosi.*",
        )
    ),
    install_requires=[
        "schema",
    ],
    python_requires=">=3.8",
    package_data={
        "configuration": ["config/*"],
        "documentation": ["docs/*"],
        "demonstration": ["demo/*"],
    },
    include_package_data=True,
    zip_safe=False,
)
