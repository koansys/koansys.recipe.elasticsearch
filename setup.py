"""Setup script."""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.getcwd(), *rnames)).read()


setup(
    name="koansys.recipe.elasticsearch",
    version=read('version.txt').strip(),
    author="Koansys, LLC",
    author_email="info@koansys.com",
    description="ZC Buildout recipe for setting up elasticsearch.",
    license="LGPL 3",
    keywords="elasticsearch zc.buildout recipe",
    url='http://pypi.python.org/pypi/koansys.recipe.elasticsearch',
    long_description=(
        read('README.txt')
        + '\n' +
        read('src', 'koansys', 'recipe', 'elasticsearch', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    package_data={'koansys.recipe.elasticsearch': ['README.txt']},
    namespace_packages=['koansys', 'koansys.recipe'],
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],
    entry_points={'zc.buildout': ['default = koansys.recipe.elasticsearch:Recipe']},
    zip_safe=False,
    )
