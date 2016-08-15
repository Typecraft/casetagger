===============================
Case Tagger
===============================


.. image:: https://img.shields.io/pypi/v/casetagger.svg
        :target: https://pypi.python.org/pypi/casetagger

.. image:: https://img.shields.io/travis/Typecraft/casetagger.svg
        :target: https://travis-ci.org/Typecraft/casetagger

.. image:: https://readthedocs.org/projects/casetagger/badge/?version=latest
        :target: https://casetagger.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/Typecraft/casetagger/shield.svg
     :target: https://pyup.io/repos/github/Typecraft/casetagger/
     :alt: Updates


Part-of-speech and morphological tagger employing a simple cased-based algorithm.


* Free software: MIT license
* Documentation: https://casetagger.readthedocs.io.


Overview
--------

The case tagger is a polyglot part-of-speech and morphological gloss-tagger. The tag-set used is the `Typecraft tag-set
<https://typecraft.org/tc2wiki/Special:TypeCraft/POSTags/>`_.

The tagger uses simple case-based learning from a large corpus to create a large database of different cases for
each language.

When tagging a phrase, the tagger fetches any relevant case for each word, and then 'merges' the cases.

Installation
-----------

    pip install casetagger

Usage
--------

    casetagger [OPTIONS]

Tagging
--------

The

Features
--------

* TODO

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

