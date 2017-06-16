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

Thereafter comes the dictionary for bathymetry settings (dictB), which are used to construct the necessary (different) bathymetries and corresponding XBeach grid files.
In here desired sizes and types of bathymetry can be specified, as well as options as for instance the ability to extend the last grid cell for a certain amount of cells.

Then comes the dictionary for other user input (dictU) regarding the types of module/tests/cases/runs and what parameters should be altered between them.

The final dictionary is regarding the applied checks in analyze_this (dictC).
There can be specified what kind of individual and comparison checks are required and what the desired constraints are.

Hereafther these dictionaries are written into txt-files.


setup
-----
The applied structure for the setup file is the use of multiple for-loops, and is altered for every different diagnostic test.
There are loops for tests/cases/runs etc which are used to make this into folder structures in which the XBeach input files can be written.
Within these loops specific parameters can be changed, according to user_input, so different XBeach input files can be created.
The desired bathymetries are made using the generic script bathy.py.
This together with the specified parameters is turned into XBeach' params.txt, x.txt, (y.txt) and z.txt files using the generic script xbeach.py.
These are stored in a specific folder together with a shell script that ensures that it can be run on the cluster.


xbeach
------
xbeach.py is part of xbeach-tools-python (https://github.com/openearth/xbeach-tools-python) which is a toolbox constructing, running and analysing XBeach models.
The script from the Python 3 branch is used, because all the other scripts are made to be compatible with Python 3 (and if possible Python 2 as well)
From this script the class XBeachModel is used to construct the XBeach input files.
For the class XBeachBathymetry the functionalities 'mirror', 'turn' and 'gridextend' are created, which are used to first extend the grid by copying the last grid cells for a specified number of times.
Thereafter the bathymetry is mirrored when specified, and the grid and bathymetry can be turn 90 degrees as well.


bathy
-----
bathy.py is a script to create different bathymetry profiles, and is shared between the diagnostic tests.
The class Bathymetry consists of multiple default values which can be overruled to the desired parameters.
The structure of the script is that you have certain 'general building blocks' and 'specific bathymetry profiles'.
The first contains general shapes as a dean profile, horizontal bottom and a linear slope as well as a function to make a grid longshore uniform.
The second contains different profiles which are combinations of the general building blocks, here you can think of a 2D dean profile or a partly horizontal and partly sloping profile.
Both parts of the script can be extended with any profile desired.

Running the scripts
-------------------
Now all XBeach input files are created they can be run on the cluster using the files runall.py, check_runs.py and clean_cluster.py.
These are based on generic scripts and do not need explanation regarding the diagnostic tests.


analyze_this
------------
After all XBeach models have run the results are stored in the specified folder structure.
Then these results are analysed using the scripts analyze_this.py which is diagnostic test specific.
The structure of the script is the same as setup.py in the way that it uses the same for-loop structure.
But in this script it reads this input structure from the dictionary txt-files created by user_input.py.
Then using these loops all the different netCDF XBeach output files are read, to get the desired parameters.

Thereafter starts a new for-loop to perform multiple checks on each netCDF file, as specified in dictionary C.
If a certain check like 'massbalance' is specified, this will be performed using checks.py.
In this generic file different kinds of checks are specified with all a specific needed input, but all with a single value as result.
If a check has a satisfactory result it gets check = 0, if the test has run but the result is unsatisfactory it gets check = 1.
When a check is called for but something went wrong it gets check = 2.

The results of all performed checks are stored in a database using database.py.
From here all checks with a value > 0 can be used to send an error message to the responsible person.

There is also the possibility to for instance make plots here and include them in the folder structure.



checks
------
checks.py is a script containing different functions to test the XBeach results, and is shared between the diagnostic tests.
It contains checks that are performed over the whole grid (e.g. a mass balance check) and checks that are performed over a certain transect (usually the middle one).
Herefore there are also some additional functions to filter out the middle transect or calculating the slope per grid cell.
The output of all checks is a single value.


database
--------
database.py is a script to make and use a database to store the results of the checks per module/test/case/run/check, and is shared between the diagnostic tests. 
It uses a SLQ type database, for now sqlite3 for Python as a local database.