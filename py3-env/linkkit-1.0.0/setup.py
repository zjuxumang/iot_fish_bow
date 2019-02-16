import setuptools

with open("README.md", mode='r', encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="linkkit",
    version="1.0.0",
    author="Linkkit Python SDK",
    author_email="",
    description="Aliyun IoT Linkkit SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
