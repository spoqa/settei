import ast
import io
import os
import os.path

from setuptools import find_packages, setup


install_requires = [
    'pytoml >= 0.1.10, < 0.2.0',
    'setuptools',
    'typeguard >= 2.2.1',
]
extras_require = {
    'flask': ['Flask', 'Werkzeug'],
    'celery': ['celery', 'kombu'],
}
all_extra_requires = [
    package
    for packages in extras_require.values()
    for package in packages
]
tests_require = [
    'pytest >= 3.6.3, < 4.0.0',
] + all_extra_requires
docs_require = [
    'Sphinx >= 1.4',
    'sphinx_rtd_theme',
] + all_extra_requires


def get_version():
    with open(os.path.join('settei', 'version.py')) as f:
        tree = ast.parse(f.read(), f.name)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
                continue
            target, = node.targets
            value = node.value
            if not (isinstance(target, ast.Name) and
                    target.id == 'VERSION_INFO' and
                    isinstance(value, ast.Tuple)):
                continue
            elts = value.elts
            if any(not isinstance(elt, ast.Num) for elt in elts):
                continue
            return '.'.join(str(elt.n) for elt in elts)


def readme():
    name = os.path.join(os.path.dirname(__file__), 'README.rst')
    try:
        with io.open(name, encoding='utf-8') as f:
            return f.read()
    except (IOError, OSError):
        return


setup(
    name='settei',
    version=get_version(),
    description='Configuration loader from a TOML file',
    long_description=readme(),
    url='https://github.com/spoqa/settei',
    license='Apache 2.0',
    author='Spoqa Creators',
    author_email='dev' '@' 'spoqa.com',
    packages=find_packages(),
    python_requires='>=3.4.0',
    install_requires=install_requires,
    extras_require=dict(
        extras_require,
        tests=tests_require,
        docs=docs_require,
    ),
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
