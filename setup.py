import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


with open(os.path.join("ralbot/ipxact", "__about__.py")) as f:
    v_dict = {}
    exec(f.read(), v_dict)
    version = v_dict['__version__']

setuptools.setup(
    name="ralbot-ipxact",
    version=version,
    author="Alex Mykyta",
    author_email="amykyta3@github.com",
    description="Convert compiled SystemRDL input into IP-XACT XML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SystemRDL/RALBot-ipxact",
    packages=['ralbot.ipxact'],
    include_package_data=True,
    install_requires=[
        "systemrdl-compiler",
    ],
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)  e",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ),
    project_urls={
        #"Documentation": "TBD",
        "Source": "https://github.com/SystemRDL/RALBot-ipxact",
        "Tracker": "https://github.com/SystemRDL/RALBot-ipxact/issues",
    },
)
