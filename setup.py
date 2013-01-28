try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

install_requires = [
    'Scrapy>=0.16.4',
    'nose==1.2.1',
]

long_description = open('README.rst').read()

setup(
    name='scrapyrwiki',
    version="0.1",
    description='A collection of helpers for running Scrapy in ScraperWiki',
    url='http://github.com/SpazioDati/scrapyrwiki',
    author='SpazioDati',
    author_email='hello@spaziodati.eu',
    packages=['scrapyrwiki'],
    zip_safe=True,
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    long_description=long_description,
    install_requires=install_requires,
)
