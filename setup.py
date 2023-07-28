from setuptools import setup, find_packages

setup(
    name='pyJMT',
    version='0.1.4',
    author='James Stadler',
    author_email='jws22@ic.ac.uk',
    packages=find_packages(exclude=["test*", "docs*"]),
    license="BSD 3-Clause",
    description='A python wrapper for Java Modelling Tools (JMT)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    projecturls={
        'Documentation': "https://imperial-qore.github.io/pyJMT/",
        "Source": "https://github.com/imperial-qore/pyJMT"
    },
    install_requires=['requests', 'setuptools', 'enum-tools'],
    python_requires='>=3.6',
)
