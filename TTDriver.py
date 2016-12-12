# -*- coding: utf-8 -*-
"""
Twenty Tester Driver - v0.1
TTDriver.py

A test driver for TT.py
Compatible with TT v1.6d0

@author: Matt Tillman

"""
### initialize
import sys
import pandas as pd
import numpy as np
from random import randint
import TT

###functions


### read setup file
inputParam = pd.read_csv('runsetup.cfg', header = 0)

totalRuns = len(inputParam)

### assign varibles passed to TT

for run in range(0,totalRuns):
    story = inputParam.story[run]
    friendfilename = inputParam.friendfile[run]
    foefilename = inputParam.foefile[run]
    outfile = inputParam.outfile[run]
    maxrounds = inputParam.maxrounds[run]
    MOSC = inputParam.MOSC[run]
    HPHR = inputParam.HPHR[run]
    critrule = inputParam.critrule[run]

### ENCOUNTER SETUP (Section moved to TTDriver)
   
    friendfile = pd.read_csv(friendfilename, header=0)
    foefile = pd.read_csv(foefilename, header = 0)

### FORMAT THE RESULTS DATAFRAME
    avgrounds = 0
    feature_list = ['Name','Count','SurvFrac']
    results = pd.DataFrame(0.0, index=np.arange(len(friendfile)+len(foefile)), columns=feature_list)

    for i in range(0,len(friendfile)):
        results.loc[i,'Name'] = friendfile.Name[i]
        results.loc[i,'Count'] = friendfile.Count[i]
        friendfile.loc[i,'ALIVE'] = friendfile.Count[i]
    for i in range(0, len(foefile)):
        results.loc[(i + len(friendfile)),'Name'] = foefile.Name[i]
        results.loc[i+len(friendfile),'Count'] = foefile.Count[i]
        foefile.loc[i,'ALIVE'] = foefile.Count[i]

### call TT and recover output

    version, avgrounds, results = TT.encounterloop(story,friendfilename,foefilename,maxrounds,MOSC,HPHR,critrule,results)

### OUTPUT RESULTS
#Clear items from the results frame that didn't fight
    results = results[results.Count != 0]

    print('Results from Twenty Tester v.' + version)
    print('After an Average of '+str(avgrounds) + ' rounds over ' + str(MOSC) + ' replicates')
    print('HPHR set to ' + str(HPHR))
    print(results)

### write output to file


### repeat

