from setuptools import setup, find_packages

setup(
    name="real-time-siem-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "scapy>=2.4.5",
        "pandas>=1.3.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "scikit-learn>=0.24.0",
    ],
    python_requires=">=3.6",
)