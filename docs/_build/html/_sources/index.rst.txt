.. xbeachtest documentation master file, created by
   sphinx-quickstart on Tue Jun 13 09:56:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to xbeachtest's documentation!
======================================

'xbeachtest' is the project where diagnostic tests are created to test the process-based model of XBeach.
The tests runs beside the current skillbed and are more focussed on specific modules of the code rather then the performance of the entire model.
Herefore the setup of the models is simple and only the relevant processes to test the module are turned on.
The idea is that by testing specific processes and functionalities of the code, more insight is created whether they still perform as intended.
Also bugs should be easier to find because of a structured development of the tests. 

The source code of the scripts can be found at https://github.com/openearth/xbeach-test-python

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Acknowledgements
================

xbeachtest is initially developed by Tim Leijnse at Deltares as part of an internship regarding 'Developing diagnostic tests for XBeach' (link to TUD repository)
xbeachtest is currently maintained by Bas Hoonhout at Deltares

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
