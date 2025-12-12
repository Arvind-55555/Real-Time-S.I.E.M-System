from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="realtime-siem",
    version="0.1.0",
    author="Arvind",
    author_email="arvind.saane.111@gmail.com",
    description="A Real-Time Security Information and Event Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arvind-55555/Real-Time-S.I.E.M-System",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "siem=realtime_siem.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "realtime_siem": ["config/*.json", "rules/*.yaml", "templates/*.j2"],
    },
)