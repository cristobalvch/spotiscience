from setuptools import setup, find_packages
import codecs
import os


from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


VERSION = '0.0.1'
DESCRIPTION = 'A Library for Data Scientist for extracting and modelling music data'

# Setting up
setup(
    name="spotiscience",
    version=VERSION,
    author="Cristobal Veas (cristobalvch)",
    author_email="<cristobal.veas.ch@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['spotipy', 'lyricsgenius','pandas','numpy','scikit-learn','spacy','en_core_web_lg@https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.0.0/en_core_web_lg-3.0.0.tar.gz#egg=en_core_web_lg',
                      'es_core_news_lg@https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.0.0/es_core_news_lg-3.0.0.tar.gz#egg=es_core_news_lg'],
    keywords=['python', 'data', 'data science', 'music', 'spotify', 'machine learning','topicmodelling','natural language processing'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
