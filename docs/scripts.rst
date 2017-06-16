Hier uitleggen hoe de scripts in het algemeen te werk gaan, bij avalanching.rst wordt de specieke implementatie voor die test besproken


Scripts
==========

In this section the general structure of all the scripts will be explained, the specific implementation for the diagnostic tests is explained in their specific sections.


user_input
----------

The applied structure for the user input file is the use of multiple dictionaries containing all desired parameters and options, and is altered for every different diagnostic test.
These different dictionaries are also exported as txt-files so the specific input is still known afterwards.
The txt-files are also used by analyze_this.py so that the analysis scripts run independent of the setup scripts.

At first there is the dictionary for parameter settings that should end up in XBeach' params.txt file (dictP).
Here parameters about which processes should be turned on or off, the grid, boundaries, output and others are specified.
The values specified here can be seen as the default settings for the designed diagnostic test.
Later some of these parameters can be varied during different tests/cases/runs.

Thereafter comes the dictionary for bathymetry settings, which are used to construct the necessary (different) bathymetries and corresponding XBeach grid files.
In here desired sizes and types of bathymetry can be specified, as well as options as for instance the ability to extend the last grid cell for a certain amount of cells.

Then comes the dictionary for other user input regarding the types of module/tests/cases/runs and what parameters should be altered between them.

The final dictionary is regarding the applied checks in analyze_this.
There can be specified what kind of individual and comparison checks are required and what the desired constraints are.

Hereafther these dictionaries are written into txt-files.


setup
-----
The applied structure for the setup file is the use of multiple for-loops, and is altered for every different diagnostic test.
There are loops for tests/cases/runs etc which are used to make this into folder structures in which the XBeach input files can be written.
Within these loops specific parameters can be changed, according to user_input, so different XBeach input files can be created.
The desired bathymetries are made using the generic script bathy.py.
This together with the specified parameters is turned into XBeach' params.txt, x.txt, (y.txt) and z.txt files using the generic script xbeach.py



xbeach
------
general




bathy
-----
general



analyze_this
------------
test specific





checks
------
general



database
--------
general