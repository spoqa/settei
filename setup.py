from setuptools import find_packages, setup


tests_require = [
    'pytest >= 2.7.0',
]
install_requires = [
    'pytoml >= 0.1.10, < 0.2.0',
    'setuptools',
    'tsukkomi >= 0.0.5',
]
docs_require = [
    'Sphinx >= 1.4',
]

setup(
    name='settei',
    version='0.1.1',
    description='Configuration loader from a TOML file',
    license='Apache 2.0',
    author='Spoqa Creators',
    author_email='dev' '@' 'spoqa.com',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
        'docs': docs_require,
    },
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
