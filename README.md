# twenty-tester
Current Version 1.6d0 Likable Lich

Developed to numerically simulate interesting features of combat in d20 games.

Files included in distribution:

TTDriver.py - sets up the parameters that will be run and handles I/O

TT.py - simulates the encounter

Friend.csv - user input csv file that defines one side of the encounter

Foe.csd - user input csv file that defines the other side of the encounter

setup.cfg - user input csv file that defines the parameters of the analysis runs

TTlogo.png - the beautiful logo for twenty-tester

Please see the GitHub wiki for information on the csv files.

RELEASE NOTES:

1.  TT.py is now driven by TTDriver.py, parameter changes for multiple runs can be set using runsetup.cfg

2.  Files in release are set up to show a sweep through an encounter of various sizes to determine what is a challenge for the party

3.  Code is sloppy, inefficient and poorly commented, but it seems to work