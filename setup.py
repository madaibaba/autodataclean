import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autodataclean",
    version="0.1.0",
    author="Alex Hou",
    author_email="houalex@gmail.com",
    description="A Python package for auto data cleaning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/madaibaba/autodataclean",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'plotly',
        'jinja2',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'autodataclean=dataclean.__main__:main',
        ],
    },
)