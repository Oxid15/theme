import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="theme-label",
    version='0.2.1',
    author='Ilia Moiseev',
    author_email='ilia.moiseev.5@yandex.ru',
    license='MIT',
    description="Simple CLI labeling tool for text classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux"
    ],
    package_dir={"theme": "./theme"},
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'numpy',
        'pandas',
    ]
)
