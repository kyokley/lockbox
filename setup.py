from setuptools import setup, find_packages
import versioneer

setup(
    name="lockbox",
    description="Simple script to encrypt a given file",
    author="Kevin Yokley",
    author_email="kyokley2@gmail.com",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={},
    scripts=["scripts/lockbox"],
    install_requires=["cryptography", "qrcode-terminal", "docopt", "blessings"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=False,
    keywords="crypto",
    classifiers=[
        "Development Status :: 5 - Released",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        # An invalid classifier disables uploads to PyPI; DevPi doesn't care.
        "Private :: Do Not Upload",
    ],
)
