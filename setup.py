from setuptools import setup


tests_require = [
    'pytest >= 2.7.0',
]
install_requires = [
    'pytoml >= 0.1.7, < 0.2.0',
    'setuptools',
    'typeannotations >= 0.1.0, < 0.2.0',
]

setup(
    name='settei',
    version='0.1.0',
    description='Configuration loader from a TOML file',
    license='Apache 2.0',
    author='Spoqa Creators',
    author_email='dev' '@' 'spoqa.com',
    py_modules=['settei'],
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
    },
    tests_require=tests_require,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
