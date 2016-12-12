# -*- coding: utf-8 -*-
"""
Twenty Tester v1.6d0 - Likable Lich
TT.py

Numerical Simulation of Combat in d20 Games

@author: Matt Tillman
"""
import sys
import pandas as pd
import numpy as np
from random import randint


### version to do
# 1.  divide TT.py 1.6d0 into functions
# A.  setup function
# B.  Loop function
# C.  results function
# D.  Eliminate timers [DONE]


### Functions

def dice(dicestr):
    """
    Provides a Roll of a Dice String (format ndX: n and X are any integers)
    """
    roll = 0
    dpos = dicestr.index('d')
    dcount = int(dicestr[0:dpos])
    dtype = int(dicestr[dpos+1:])
    for n in range(0,dcount):
        throw = randint(1,dtype)
        roll = throw + roll
    return roll

def condcheck(side):
    """
    Determines the combat condition of the force.  1 = Melee fighters left, 2 = no melee, ranged left, 3 = no melee or ranged, only spells
    """
    for n in range(0,len(side)):
        if (side.PrefType[n] == 'M' and side.ALIVE[n] > 0):
            return 1
    for n in range(0,len(side)):
        if (side.PrefType[n] == 'R' and side.ALIVE[n] > 0):
            return 2
    return 3

def rangeclose(side,pos):
    """
    Determines range to closest ALIVE enemy targets
    """
    ranges = []
    #only look at side.ALIVE !=0
    tempside = side[side.ALIVE != 0]
    if tempside.empty:
        return 0
    else:
        for n in range(0,len(tempside)):
            ranges.append(abs(pos - tempside.POS.iloc[n]))
        return min(ranges)

def hprem(side):
    """
    Determines how many HP are left on a particular side (takes into account multiple survivors per group)
    """
    #try to do it easily first
    if (side.Count.sum() == len(side)):
        return side.WHP.sum()
    else:
        hpsum = 0
        for n in range(0, len(side)):
            if side.ALIVE[n] == 0:
                rowhp = 0
            else:
                rowhp = side.HP[n]*(side.ALIVE[n] - 1) + side.WHP[n]
            hpsum = hpsum + rowhp
        return hpsum

def critdam(num,die):
    """
    A poor use of a Python function to be sure, the purpose was to clearly identify where the critical damage mechanic was in the code so that users could modify
    with their own if desired (in this case, the parameter passed is simply an index that determines which critical damage rule is applied, while die is the
    damage die that is being rolled for the damage in question).  Note that this function does NOT add the bonus damage.
    """
    #num = 1 will represent 1 extra damage die
    if num == 1:
        dam = dice(die) + dice (die)
    #num = 2 will represent a 50% chance of no extra damage, 35% chance of 1 extra die, 15% chance of 2 extra dice
    elif num ==2:
        roll = dice('1d10') + dice('1d10')*10
        if roll <= 50:
            dam = dice(die)
        elif roll <= 85:
            dam = dice(die) + dice(die)
        else:
            dam = dice(die) + dice(die) + dice(die)
    return dam



def encounterloop(story,friendfilename,foefilename,maxrounds,MOSC,HPHR,critrule,results):
    """
    The function at the heart of TT.py.  Called from TTDriver.py
    """
    version = '1.6d0 - Likable Lich' 
    OSC = 1
    avgrounds = 0
    for OSC in range (1, MOSC+1):
        
    
        friend = pd.read_csv(friendfilename, header=0)
        foe = pd.read_csv(foefilename, header = 0)
        
        for i in range(0,len(friend)):
            friend.loc[i,'ALIVE'] = friend.Count[i]
        for i in range(0,len(foe)):
            foe.loc[i,'ALIVE'] = foe.Count[i]
    
        friendcount = friend.ALIVE.sum()
        foecount = foe.ALIVE.sum()
        friendcond = condcheck(friend)
        foecond = condcheck(foe)
    
    
        ### INITIATIVE SECTION
    
        if story=='verbose':
            print('Rolling for initiative')
        totalgroups = len(foe) + len(friend)
    
        for i in range(0, len(friend)):
            initroll = dice('1d20') + friend.IB[i]
            friend.loc[i,'ORDER'] = initroll
    
        for i in range(0, len(foe)):
            initroll = dice('1d20') + foe.IB[i]
            foe.loc[i,'ORDER'] = initroll
    
        rmax = max(friend.ORDER)
        omax = max(foe.ORDER)
        imax = max(omax,rmax)
    
        initorder = []
    
        for i in range (0,imax+1):
            for j in range(0,len(friend)):
                if friend.ORDER[j] == i:
                    initorder.append([0,j])
            for k in range (0,len(foe)):
                if foe.ORDER[k] == i:
                    initorder.append([1,k])
    
        ### ENCOUNTER CALCULATIONS
    
        for round in range(0,maxrounds):
            if story=='verbose':
                print('***** ROUND '+str(round+1) + ' *****')
            for unit in range(0, len(initorder)):
                #set unit active
                initside,activeunit = initorder[unit]
                if initside == 0:
                    activeside = friend
                    oppside = foe
                    direction = 1
                else:
                    activeside = foe
                    oppside = friend
                    direction = -1
                #### section to skip those who are no longer alive (or no longer undead?)
                if activeside.ALIVE[activeunit] == 0:
                    continue
    
                if story=='verbose':
                    print('*** ' + activeside.Name[activeunit]+' Turn')
                #MOVEMENT
                if story=='verbose':
                    print('Movement Phase')
                #determine if enemy is ALIVE!!! in current grid
                if rangeclose(oppside, activeside.POS.iloc[activeunit]) == 0:
                    #check for spellcaster
                    if activeside.PrefType[activeunit] == 'S':
                        #retreat
                        newPOS = activeside.POS.iloc[activeunit] - direction
                        activeside.loc[activeunit,'POS'] = newPOS
                else:
                    #check for melee fighter
                    if activeside.PrefType[activeunit] == 'M':
                        #advance
                        newPOS = activeside.POS.iloc[activeunit] + direction
                        activeside.loc[activeunit,'POS'] = newPOS
                    else:
                        #check range for S and R
                        if rangeclose(oppside, activeside.POS.iloc[activeunit])>2:
                            #advance
                            newPOS = activeside.POS.iloc[activeunit] + direction
                            activeside.loc[activeunit,'POS'] = newPOS
    
                #healing should be an alternate action to attacking, need to make the healing decision first, then make combat an else
                if ((activeside.WHP[activeunit]/activeside.HP[activeunit]) < HPHR and activeside.HEALCOUNT[activeunit] > 0):
                    heal = dice(activeside.HEAL[activeunit])
                    activeside.loc[activeunit,'WHP'] = min(activeside.WHP[activeunit] + heal, activeside.HP[activeunit])
                    activeside.loc[activeunit,'HEALCOUNT'] = activeside.HEALCOUNT[activeunit] - 1
                    if story == 'verbose':
                        print('Healing Action - New HP: '+str(activeside.WHP[activeunit]))
    
    
                else:
                    #COMBAT
                    #IF ENEMY IS IN CURRENT SQUARE MELEE
                    if rangeclose(oppside, activeside.POS[activeunit]) == 0:
                        if story=='verbose':
                            print('Melee Combat Action')
                        for i in range(0,activeside.ALIVE[activeunit]):
                            targettemp = oppside.loc[oppside.POS == activeside.POS[activeunit]]
                            if (targettemp.ALIVE.sum() > 0):
                                targets = targettemp.loc[targettemp.ALIVE != 0]
                            else:
                                break
                            #draw a random target assignment
                            targetunit = randint(0,len(targets)-1)
                            targetname = targets.Name.iloc[targetunit]
                            if story=='verbose':
                                print('Target: '+str(targets.Name.iloc[targetunit]) + ' (' +str(targets.ALIVE.iloc[targetunit]) + ')')
                            damage = 0
                            #attack
                            attackroll = dice('1d20') + activeside.MAB[activeunit]
                            #damage
                            if (attackroll - activeside.MAB[activeunit]) == 20:
                                if story == 'verbose':
                                    print('Critical Hit')
                                damage = critdam(critrule,activeside.MDAM1[activeunit]) + activeside.MDAMB[activeunit]
                            elif (attackroll >= targets.AC.iloc[targetunit]):
                                if story == 'verbose':
                                    print('Target Hit')
                                damage = dice(activeside.MDAM1[activeunit]) + activeside.MDAMB[activeunit]
    
                            #attrition
                            if (story == 'verbose' and damage !=0):
                                print('Damage: '+str(damage))
                            if (story=='verbose' and damage == 0):
                                print('Target Missed')
                            if damage >= targets.WHP.iloc[targetunit]:
                                targets.loc[targets.Name==targetname,'ALIVE'] = targets.ALIVE.iloc[targetunit] - 1
                                if story=='verbose':
                                    print('One '+ str(targetname) +' killed, new count: '+str(targets.ALIVE.iloc[targetunit]))
                                if targets.ALIVE.iloc[targetunit] == 0:
                                    targets.loc[targets.Name==targetname,'WHP'] = 0
                                else:
                                    targets.loc[targets.Name==targetname,'WHP'] = targets.HP.iloc[targetunit]
                            else:
                                targets.loc[targets.Name==targetname,'WHP'] = targets.WHP.iloc[targetunit] - damage
                                if (story=='verbose' and damage !=0):
                                    print('One ' + str(targetname) +' damaged, new HP: '+str(targets.WHP.iloc[targetunit]))
    
                            #multi attack
                            if activeside.MATTCNT[activeunit] > 1:
                                if story == 'verbose':
                                    print('Second melee attack')
                                #repeat entire melee process for multi attack (including target sort)
                                targettemp = oppside.loc[oppside.POS == activeside.POS[activeunit]]
                                if (targettemp.ALIVE.sum() > 0):
                                    targets = targettemp.loc[targettemp.ALIVE != 0]
                                else:
                                    break
                                #draw a random target assignment
                                targetunit = randint(0,len(targets)-1)
                                targetname = targets.Name.iloc[targetunit]
                                if story=='verbose':
                                    print('Target: '+str(targets.Name.iloc[targetunit]) + ' (' +str(targets.ALIVE.iloc[targetunit]) + ')')
                                damage = 0
                                #attack
                                attackroll = dice('1d20') + activeside.MAB[activeunit]
                                #damage
                                if (attackroll - activeside.MAB[activeunit]) == 20:
                                    if story=='verbose':
                                        print('Critical Hit')
                                    damage = critdam(critrule,activeside.MDAM1[activeunit]) + activeside.MDAMB[activeunit]
                                elif (attackroll >= targets.AC.iloc[targetunit]):
                                    if story=='verbose':
                                        print('Target Hit')
                                    damage = dice(activeside.MDAM1[activeunit]) + activeside.MDAMB[activeunit]
    
                                #attrition
                                if (story=='verbose' and damage !=0):
                                    print('Damage: '+str(damage))
                                if (story=='verbose' and damage == 0):
                                    print('Target Missed')
                                if damage >= targets.WHP.iloc[targetunit]:
                                    targets.loc[targets.Name==targetname,'ALIVE'] = targets.ALIVE.iloc[targetunit] - 1
                                    if story=='verbose':
                                        print('One '+ str(targetname) +' killed, new count: '+str(targets.ALIVE.iloc[targetunit]))
                                    if targets.ALIVE.iloc[targetunit] == 0:
                                        targets.loc[targets.Name==targetname,'WHP'] = 0
                                    else:
                                        targets.loc[targets.Name==targetname,'WHP'] = targets.HP.iloc[targetunit]
                                else:
                                    targets.loc[targets.Name==targetname,'WHP'] = targets.WHP.iloc[targetunit] - damage
                                    if (story=='verbose' and damage !=0):
                                        print('One ' + str(targetname) +' damaged, new HP: '+str(targets.WHP.iloc[targetunit]))
    
                            #unit turn over
                            if story=='verbose':
                                print('Unit turn complete, restoring data frames')
                            if initside == 0:
                                foe.loc[foe.Name==targets.Name.iloc[targetunit],'WHP'] =  targets.WHP.iloc[targetunit]
                                foe.loc[foe.Name==targets.Name.iloc[targetunit],'ALIVE'] =  targets.ALIVE.iloc[targetunit]
                            else:
                                friend.loc[friend.Name==targets.Name.iloc[targetunit],'WHP'] =  targets.WHP.iloc[targetunit]
                                friend.loc[friend.Name==targets.Name.iloc[targetunit],'ALIVE'] =  targets.ALIVE.iloc[targetunit]
    
                    #IF ENEMY IS IN RANGED TARGET SQUARE
                    elif (rangeclose(oppside, activeside.POS[activeunit]) <= 2 and rangeclose(oppside, activeside.POS[activeunit]) > 0 and activeside.PrefType[activeunit] == 'R'):
                        if story=='verbose':
                            print('Ranged Combat Action')
                        for i in range(0,activeside.ALIVE[activeunit]):
                            targetrange = rangeclose(oppside, activeside.POS[activeunit])
                            targetpos = targetrange * direction + activeside.POS[activeunit]
                            targettemp = oppside.loc[oppside.POS == targetpos]
                            if (targettemp.ALIVE.sum() > 0):
                                targets = targettemp.loc[targettemp.ALIVE != 0]
                            else:
                                break
                            #draw a random target assignment from the acceptable targets
                            targetunit = randint(0,len(targets)-1)
                            targetname = targets.Name.iloc[targetunit]
                            if story=='verbose':
                                print('Target: '+str(targets.Name.iloc[targetunit]) + ' (' +str(targets.ALIVE.iloc[targetunit]) + ')')
                            damage = 0
                            #attack
                            attackroll = dice('1d20') + activeside.RAB[activeunit]
                            #damage
                            if (attackroll - activeside.RAB[activeunit]) == 20:
                                if story=='verbose':
                                    print('Critical Hit')
                                damage = critdam(critrule,activeside.RDAM1[activeunit]) + activeside.RDAMB[activeunit]
                            elif (attackroll >= targets.AC.iloc[targetunit]):
                                if story=='verbose':
                                    print('Target Hit')
                                damage = dice(activeside.RDAM1[activeunit]) + activeside.RDAMB[activeunit]
    
                            #attrition
                            if (story=='verbose' and damage != 0):
                                print('Damage: '+str(damage))
                            if (story=='verbose' and damage == 0):
                                print('Target Missed')
                            if damage >= targets.WHP.iloc[targetunit]:
                                targets.loc[targets.Name==targetname,'ALIVE'] = targets.ALIVE.iloc[targetunit] - 1
                                if story=='verbose':
                                    print('One '+ str(targetname) +' killed, new count: '+str(targets.ALIVE.iloc[targetunit]))
                                if targets.ALIVE.iloc[targetunit] == 0:
                                    targets.loc[targets.Name==targetname,'WHP'] = 0
                                else:
                                    targets.loc[targets.Name==targetname,'WHP'] = targets.HP.iloc[targetunit]
                            else:
                                targets.loc[targets.Name==targetname,'WHP'] = targets.WHP.iloc[targetunit] - damage
                                if (story=='verbose' and damage !=0):
                                    print('One ' + str(targetname) +' damaged, new HP: '+str(targets.WHP.iloc[targetunit]))
    
                            #multi attack repeat entire attack cycle
                            if activeside.RATTCNT[activeunit] > 1:
                                if story == 'verbose':
                                    print('Second ranged attack')
                                targetrange = rangeclose(oppside, activeside.POS[activeunit])
                                targetpos = targetrange * direction + activeside.POS[activeunit]
                                targettemp = oppside.loc[oppside.POS == targetpos]
                                if (targettemp.ALIVE.sum() > 0):
                                    targets = targettemp.loc[targettemp.ALIVE != 0]
                                else:
                                    break
                                #draw a random target assignment from the acceptable targets
                                targetunit = randint(0,len(targets)-1)
                                targetname = targets.Name.iloc[targetunit]
                                if story=='verbose':
                                    print('Target: '+str(targets.Name.iloc[targetunit]) + ' (' +str(targets.ALIVE.iloc[targetunit]) + ')')
                                damage = 0
                                #attack
                                attackroll = dice('1d20') + activeside.RAB[activeunit]
                                #damage
                                if (attackroll - activeside.RAB[activeunit]) == 20:
                                    if story=='verbose':
                                        print('Critical Hit')
                                    damage = critdam(critrule,activeside.RDAM1[activeunit]) + activeside.RDAMB[activeunit]
                                elif (attackroll >= targets.AC.iloc[targetunit]):
                                    if story=='verbose':
                                        print('Target Hit')
                                    damage = dice(activeside.RDAM1[activeunit]) + activeside.RDAMB[activeunit]
    
                                #attrition
                                if (story=='verbose' and damage != 0):
                                    print('Damage: '+str(damage))
                                if (story=='verbose' and damage == 0):
                                    print('Target Missed')
                                if damage >= targets.WHP.iloc[targetunit]:
                                    targets.loc[targets.Name==targetname,'ALIVE'] = targets.ALIVE.iloc[targetunit] - 1
                                    if story=='verbose':
                                        print('One '+ str(targetname) +' killed, new count: '+str(targets.ALIVE.iloc[targetunit]))
                                    if targets.ALIVE.iloc[targetunit] == 0:
                                        targets.loc[targets.Name==targetname,'WHP'] = 0
                                    else:
                                        targets.loc[targets.Name==targetname,'WHP'] = targets.HP.iloc[targetunit]
                                else:
                                    targets.loc[targets.Name==targetname,'WHP'] = targets.WHP.iloc[targetunit] - damage
                                    if (story=='verbose' and damage !=0):
                                        print('One ' + str(targetname) +' damaged, new HP: '+str(targets.WHP.iloc[targetunit]))
                            #unit turn over
                            if story=='verbose':
                                print('Unit turn complete, restoring data frames')
                            if initside == 0:
                                foe.loc[foe.Name==targets.Name.iloc[targetunit],'WHP'] =  targets.WHP.iloc[targetunit]
                                foe.loc[foe.Name==targets.Name.iloc[targetunit],'ALIVE'] =  targets.ALIVE.iloc[targetunit]
                            else:
                                friend.loc[friend.Name==targets.Name.iloc[targetunit],'WHP'] =  targets.WHP.iloc[targetunit]
                                friend.loc[friend.Name==targets.Name.iloc[targetunit],'ALIVE'] =  targets.ALIVE.iloc[targetunit]
    
                    #IF ENEMY IS IN SPELL TARGET SQUARE SPELL (make work with type S anywhere on the battlefield)
                    elif (activeside.PrefType[activeunit] == 'S'):
                        if story=='verbose':
                            print('Spell Combat Action')
                        for i in range(0,activeside.ALIVE[activeunit]):
                            targetrange = rangeclose(oppside, activeside.POS[activeunit])
                            targetpos = targetrange * direction + activeside.POS[activeunit]
                            targettemp = oppside.loc[oppside.POS == targetpos]
                            if (targettemp.ALIVE.sum() > 0):
                                targets = targettemp.loc[targettemp.ALIVE != 0]
                            else:
                                break
                            #draw a random target assignment from the acceptable targets
                            targetunit = randint(0,len(targets)-1)
                            targetname = targets.Name.iloc[targetunit]
                            if story=='verbose':
                                print('Target: '+str(targets.Name.iloc[targetunit]) + ' (' +str(targets.ALIVE.iloc[targetunit]) + ')')
                            damage = 0
                            #no attack roll for spells assumed
                            #damage
                            #select which spell is being cast
                            #prioritize high damage (spell 2) then medium (spell 1) then cantrip
                            if activeside.SCOUNT2[activeunit] > 0:
                                damage = dice(activeside.SDAM2[activeunit])
                                activeside.loc[activeunit,'SCOUNT2'] = activeside.SCOUNT2[activeunit] - 1
                                if story == 'verbose' :
                                    print('Spell Type 2 Cast')
                            elif activeside.SCOUNT1[activeunit] > 0:
                                damage = dice(activeside.SDAM1[activeunit])
                                activeside.loc[activeunit,'SCOUNT1'] = activeside.SCOUNT1[activeunit] - 1
                                if story == 'verbose':
                                    print('Spell Type 1 Cast')
                            else:
                                damage = dice(activeside.CTRIPDAM[activeunit])
                                if story == 'verbose':
                                    print('Cantrip Cast')
                            #multi attack not implemented for spells in 1.0
                            #attrition
                            if (story=='verbose' and damage != 0):
                                print('Damage: '+str(damage))
                            if (story=='verbose' and damage == 0):
                                print('Target Missed')
                            if damage >= targets.WHP.iloc[targetunit]:
                                targets.loc[targets.Name==targetname,'ALIVE'] = targets.ALIVE.iloc[targetunit] - 1
                                if story=='verbose':
                                    print('One '+ str(targetname) +' killed, new count: '+str(targets.ALIVE.iloc[targetunit]))
                                if targets.ALIVE.iloc[targetunit] == 0:
                                    targets.loc[targets.Name==targetname,'WHP'] = 0
                                else:
                                    targets.loc[targets.Name==targetname,'WHP'] = targets.HP.iloc[targetunit]
                            else:
                                targets.loc[targets.Name==targetname,'WHP'] = targets.WHP.iloc[targetunit] - damage
                                if story=='verbose':
                                    print('One ' + str(targetname) +' damaged, new HP: '+str(targets.WHP.iloc[targetunit]))
                            if story=='verbose':
                                print('Unit turn complete, restoring data frames')
                            if initside == 0:
                                foe.loc[foe.Name==targets.Name.iloc[targetunit],'WHP'] =  targets.WHP.iloc[targetunit]
                                foe.loc[foe.Name==targets.Name.iloc[targetunit],'ALIVE'] =  targets.ALIVE.iloc[targetunit]
                            else:
                                friend.loc[friend.Name==targets.Name.iloc[targetunit],'WHP'] =  targets.WHP.iloc[targetunit]
                                friend.loc[friend.Name==targets.Name.iloc[targetunit],'ALIVE'] =  targets.ALIVE.iloc[targetunit]
    
            #character turn over, back to book keeping
    
            if friend.ALIVE.sum() == 0:
                break
            if foe.ALIVE.sum() == 0:
                break
                #NEED TO TERMINATE WHEN ONE SIDE IS DEAD
    
        friendsurvive = friend.ALIVE.sum()
    
        foesurvive = foe.ALIVE.sum()
    
        if (story == 'verbose' or story =='summary'):
            print('After ' + str(round+1) + ' rounds')
            print('Friend Summary: ')
            for l in range(0,len(friend)):
                print(str(friend.Name[l]) + ': ' + str(friend.ALIVE[l]) + '/' +str(friend.Count[l])+' alive with ' + str(friend.WHP[l]) + ' HP remaining for most injured')
            print('Foe Summary: ')
            for l in range(0,len(foe)):
                print(str(foe.Name[l]) + ': ' + str(foe.ALIVE[l]) + '/' +str(foe.Count[l])+' alive with ' + str(foe.WHP[l]) + ' HP remaining for most injured')
    
        #RECORD RESULTS
        #average number of rounds
        avgrounds = (avgrounds * (OSC-1) + round)/OSC
    
        #survival percentages
    
        for i in range(0,len(friend)):
            results.loc[i,'SurvFrac'] = (results.SurvFrac[i]*(OSC-1)*friend.Count[i]+friend.ALIVE[i])/(OSC*friend.Count[i])
        for i in range(0, len(foe)):
            results.loc[(i + len(friend)),'SurvFrac'] = (results.SurvFrac[i + len(friend)]*(OSC-1)*foe.Count[i]+foe.ALIVE[i])/(OSC*foe.Count[i])

    return version, avgrounds, results


