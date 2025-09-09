from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="cms-nbi-client",
    version="0.1.0",
    description="Python Module to interact with the Calix Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="somenetworking",
    author_email="andrewshea06@gmail.com",
    maintainer="somenetworking",
    maintainer_email="andrewshea06@gmail.com",
    url="https://github.com/somenetworking/CMS-NBI-Client",
    keywords=["CMS", "Calix", "NETCONF", "API", "Networking", "Automation", "NBI"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Networking",
        "Intended Audience :: Telecommunications Industry",
    ],
    license="GPL v3.0",
    package_dir={
        "cmsnbiclient": "src/cmsnbiclient",
        "cmsnbiclient.E7": "src/cmsnbiclient/E7",
        "cmsnbiclient.REST": "src/cmsnbiclient/REST",
    },
    packages=["cmsnbiclient", "cmsnbiclient.E7", "cmsnbiclient.REST"],
    install_requires=["xmltodict >=0.13.0", "requests >=2.28.0", "pydash >=5.1.0"],
    python_requires=">=3.7",
)
