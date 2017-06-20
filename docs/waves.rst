Diagnostic test for Waves 
=========================
(under construction)


Zeggen dat ie nog niet volledig uitontwikkeld is, voorbeelden noemen wat nog gedaan moet worden en hoe het uitgebreid kan worden



In this section the implementation of the general setup of scripts as explained in 'Scripts' for the testing of the module Waves will be explained.

Model setup
-----------
The goal is to setup a model to check whether waves are created and propagated correctly. 
The test is not fully developped yet but the first setup is implemented.
After collaboration the first setup focusses on the Surfbeat mode of XBeach in combination with different lateral boundary conditions.
Herefore the hydrodynamic processes 'swave' and 'lwave' are turned on (just as flow for now) and morphodynamic processes as 'sedtrans', 'morphology' and 'avalanching' are turned off.

The bathymetry consists of a Dean profile from -15m to +2m, after which there is a steeper linear dune slope of 0.1. 
For now the grid is equidistant with dx=10m and dy=20m, but it is advised to make 'dx' depth dependent to optimise the internal timestep of XBeach because of the CFL conditions (not yet implemented, can be done as in OET: xb_grid_xgrid.m)

For the boundaries 'front' is set to 'abs_2d', 'back' is set to 'wall', 'left' and 'right' are the default of 'neumann' and 'lateralwave' is altered between 'cyclic', 'neumann' and 'wavecrest'. Furthermore
As in the avalanching test also the combination with MPI is tested, but now only the 2D options 'm1n1' (the benchmark) 'm3n1', 'm1n3' and 'm3n3' are used because the addition of 1D runs is no added value.

Because wave are now added to the XBeach model, a wave spectrum should be specified. For this the commonly used Jonswap spectrum is added, with a seperate input file called jonswap.txt.
In here a wave height Hm0 of 3m is specified, together with Tp=8s, an altering wave angle 'mainang', an altering value for 's' and the XBeach default values of gammajsp= 3.3 and fnyq= 0.3.

The things that are tested for now is the performance of XBeach Surfbeat under different wave angles, Jonswap spectra, lateral boundaries and MPI configurations.
This leads to the following folder structure: tests('neumann', 'cyclic', 'wavecrest'), cases('mainang_240', 'mainang_270', 'mainang_300'), the new layer subcases('s_10', 's_100000') and runs('benchmark','m3n1','m1n3','m3n3').
So an extra layer called subcases is added to change the parameter 's' of the Jonswap spectrum, for the large value of 100000 you get a spectrum of only one frequency and thus monochromatic waves and 10 is the default value in XBeach.

So compared to the avalanching test there are less parameter changes, different cases and exceptions, which makes the setup and analysis a lot cleaner.
In the paragraphs below notable input of the specific scripts is mentioned, if it is not yet adressed above. 
All the scripts and their input can be found at https://github.com/openearth/xbeach-test-python/xbeachtest.


user_input_waves
----------------

The biggest difference here is the addition of a new dictionary W, used for the wave input to create the Jonswap spectrum  in setup_waves.py.
Another is a smaller value for 'tintg' because a higher resolution in time is needed and the addition of more variables to 'nglobalvar'.
Another thing to notice is that the parameter 'cyclic' is varied along the tests. 
For the test 'cyclic', cyclic= 0 but for the other tests cyclic= 0.

setup_waves
-----------

Here the extra loop for subcases is added, a different bathymetry profile is called for (dean1_2d) and there is now a section which writes the jonswap.txt files to the specific folder.


analyze_this_waves
------------------

Here also the extra loop for subcases is added, as well as reading out of more variables from the netCDF files.
Hereafter there are a number of new or differenly applied tests.
The check 'bedlevelchange' is used twice, one to look if 'zb' does not change during running as you would expect and one to look if 'zs' does change during running because of created waves.
The check 'massbalance' is also used twice, one used on 'zb' to look if no sediment is somehow dissapearing (the boundaries are now open) and one to look at 'zs' to look at the water mass.
For this last purpose also a new check is created 'massbalance_intime', which looks at the output steps if the mass balance is not too much up. 
This can also be used to plot this behaviour in time.
Thereafter you get the two checks of 'wave_generation', where there is at first looked at the offshore boundary whether means of variables H, ue, ve, ui and vi are not zero (indicating that no waves are created). 
Then this also done for a location close to the coast to see if waves arrive over there.
Note that ui and vi are only created at the offshore boundary so these are not checked.
At last there is now the check 'n_Hrms' which looks along the grid cells of the n-direction whether there is a large deviation in mean Hrms along the m-transect compared to the mean Hrms of the whole grid.
Besides the output 'check' also 'Hmean_ratio' is an output which can be and is plotted.

At least one more test should be added to in some way compare the results of the benchmark with that of the other runs.
But their can probabaly be also thought of other individual checks that could be usefull.

(temporary) After all these checks there are now 3 figures that are created per run.
In the first the result of 'Hmean_ratio' is plotted along the y-axis to give more insight in the results.
The second figure containts a snap shot of the Hrms on the last timestep, which gives insight in the wave direction, wave groupiness and shadow zone.
The last figure plot the massbalance of 'zs' in time, which gives insight in the amount of water entering and leaving the model.

checks
------

For the avalanching diagnostic test the checks  'massbalance_intime', 'wave_generation and 'n_Hrms' were created.


database
--------
The database is slightly altered to facility the addition of subcases.

