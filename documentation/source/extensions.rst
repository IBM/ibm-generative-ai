IBM Generative AI Extensions Guide
==================================

Open-source contributors are welcome to extend IBM Gen AI functionality via extensions that must keep the IBM Gen AI package as a dependency. This document explains what extensions are, the types of extensions that exist, and how to create them.

.. contents::
   :local:
   :class: this-will-duplicate-information-and-it-is-still-useful-here

IBM Generative AI Core Package
------------------------------

`IBM Generative AI open-source repository <https://github.com/IBM/ibm-generative-ai>`_ lives under `IBM Github organization <https://github.com/IBM/>`_. This repository is the official and unique location of IBM Gen AI core package source code.

What is an IBM Generative AI Extension?
---------------------------------------

An extension is a software add-on that is installed on a program to enhance its capabilities. Gen AI extensions are meant to expand the capabilities of the Gen AI core package.

IBM Generative AI Extension types
---------------------------------

IBM Generative AI extensions can be either of the following:

- official open-source extensions (supported by the project team)
- third-party open-source extensions

Open-source "Gen AI official" extensions
----------------------------------------

Extensions are meant for public use from the get-go developed as official open-source extensions.

Ownership and location
++++++++++++++++++++++
Open-source official extensions are typically developed by the Gen AI team, or in collaboration with them. Providing maintenance to open-source official extensions is responsability of the Gen AI team.

Open-source "third-party" extensions
------------------------------------

All other extensions neither implemented nor officially maintained by the Gen AI team are referred to as open-source third-party extensions.

Ownership and location
++++++++++++++++++++++
Maintaining these extensions would be the responsibility of their owners.

Extensions migration
--------------------

Extensions might be migrated from one type to another upon evaluation.

Open-source "third-party" to open-source "Gen AI official"
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If open-source third-party contributors have an interest in their extensions becoming official, they must contact the IBM Gen AI team.

Open-source "Gen AI official" to Gen AI's core
+++++++++++++++++++++++++++++++++++++++++++++++

Upon evaluation of the Gen AI maintenance team, open-source extensions could be merged with Gen AI core code and become deprecated as extensions.

Design considerations to build extensions
-----------------------------------------

Among other patterns, a developer should consider a mix-and-match of the two following important development experience patterns to design an extension for IBM Gen AI SDK:

Extensions that simulate being part of a core class
+++++++++++++++++++++++++++++++++++++++++++++++++++

In spite of the extension's code living in a separate location, **try to give the impression that extended functionality is part of an IBM Gen AI core class**.

Extensions that wrap core class functionality
+++++++++++++++++++++++++++++++++++++++++++++

Designing extensions that do not integrate, but **wrap functionality in Gen AI's core** for common use cases. These classes are meant to be used as entities on their own.
