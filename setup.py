from setuptools import setup, find_packages

setup(
    name = "django-sis",
    version = "1.0",
    author = "David Burke",
    author_email = "david@burkesoftware.com",
    description = ("Django School Information System"),
    license = "GPLv3",
    keywords = "django school",
    url = "https://github.com/burke-software/django-sis",
    packages=find_packages(),
    include_package_data=True,
    test_suite='setuptest.setuptest.SetupTestSuite',
    tests_require=(
        'django-setuptest',
    ),
    install_requires = [
        'django',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python',
        "License :: OSI Approved :: GPLv3 License",
    ],
)
