from setuptools import setup, find_packages


setup(
    name='clics',
    version='0.0',
    description='clics',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='MPI EVA DLCE Dev',
    author_email='dlce.rdm@eva.mpg.de',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyclics>=3.0.1',
        'clldutils>=3.5',
        'clld>=9.2.1',
        'clld-glottologfamily-plugin>=3.1',
        'clldmpg>=4.2',
        'sqlalchemy',
        'waitress',
    ],
    extras_require={
        'dev': [
            'pyclics>=3.0.1',
            'flake8',
            'tox',
            'pydplace',
        ],
        'test': [
            'psycopg2-binary',
            'mock',
            'pytest',
            'pytest-clld>=0.4',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    test_suite="clics",
    entry_points={
        'paste.app_factory': [
            'main=clics:main',
        ]
    },
)
