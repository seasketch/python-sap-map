Heatmap package
========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install.md
   algorithm.md
   publications.md
   api.rst
   contributing.md

Overview
========

The `heatmap` package provides multiple methods of producing heatmaps including `count`, `area`, and `sap`.

.. image:: img/survey-sap-start-end.png

The `sap` method is also known as Spatial Access Priority mapping, which takes areas identified as as important, and combines them into a map of `spatial access priorities (SAP)`
This aggregate map is used in area-based planning exercises for identifying where important areas exist and measuring the impact if changes in access are made.

Common questions heatmaps can answer include:

* Where are things occurring
* Which geographic areas are important to the group?  The most important?  The least important?
* Is area A of more value to the group than area B?  How much more?
* If the use of a given area is changed, will people be impacted?  How much of the groups value is within this area?
