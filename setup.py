from setuptools import setup

setup(
    name="bridge-hub",
    version="0.1.0",
    description="GeoCat Bridge Hub",
    author="GeoCat B.V.",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["bridgehub"],
    include_package_data=True,
    install_requires=[
        "bottle",
        "lxml",
    ],
    entry_points={
        "console_scripts": [
            "bridge=bridgehub.api:main"
        ]
    }
)
