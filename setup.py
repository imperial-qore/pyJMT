from setuptools import setup, find_packages

setup(
    name='pyJMT',
    version='0.1.2',
    author='James Stadler',
    author_email='jws22@ic.ac.uk',
    packages=find_packages(exclude=["test*", "docs*"]),
    license="MIT",
    description='A python wrapper for Java Modelling Tools (JMT)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # projecturls={
    #     'Documentation': "",
    #     "Source": ""
    # },
    # url='https://github.com/yourusername/my_package',
    install_requires=['requests', 'setuptools', 'enum-tools'],
    python_requires='>=3.6',
)
