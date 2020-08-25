###############################################################################
###############################################################################
##                                                                           ##
##  THATCHORD BY TOM CONTI-LESLIE                                   find.py  ##
##                                                                           ##
##  This script takes a list of notes and some technical parameters, and     ##
##  outputs a list of lists of frets which correspond to all ways of         ##
##  playing the chord. It's where the magic happens!                         ##
##                                                                           ##
##                                                                           ##
##  License: CC BY-SA 4.0                                                    ##
##                                                                           ##
##  Contact: tom (dot) contileslie (at) gmail (dot) com                      ##
##                                                                           ##
###############################################################################
###############################################################################


# import error messages
from errors import err

# import ranking functions
import rank

def increment(maxes, current):
    """
    Helper function for incrementing a list of indices, 'current', by
    increasing the first index if possible, and if not, the next one, etc.
    (analogous to little endian)
    
    The max value for each position is that value in the list 'maxes'.
    
    N.B. modifies input 'current'.
    """
    for i in range(len(maxes)):
        if not current[i] == maxes[i] - 1:
            current[i] += 1
            return
        current[i] = 0

def smart_increment(maxes, current, chordset, stringset):
    # Our current attempt is current. How many notes does that attempt play?
    # How many notes does our chord need? If there is a gap of k notes between
    # the two, then we need to change at least the first k counters.
    k = len(chordset) - len(stringset)
    # if n is 0 or 1 then we don't need to skip anything; just increment
    # normally.
    k = max(k - 1, 0)
    for i in range(k):
        current[i] = 0

    for i in range(k, len(maxes)):
        if not current[i] == maxes[i] - 1:
            current[i] += 1
            break
        current[i] = 0
    # the counter i will now be set at the number of the rightmost string
    # changed. Return this to the main loop to update the chordset.
    return i
            

def insert(options, frets, index, r):
    """
    N.B. modifies options in place.
    Inserts frets into options if the rank of frets is lower than some of the
    current options. Pushes the worse options out of the list.
    r is the calculated rank of the option 'frets'.
    """
    tup = (frets, r)
    # start at worse end of list, move all the way to where r is in order
    l = len(options)
    i = l
    while i > 0 and r < options[i - 1][1]:
        i -= 1
    if l < index:
        # in this case, options has not yet reached full size. Just add the opt
        options.insert(i, tup)
    elif i < l:
        # in this case, options is full. Add only if our option beats at least
        # one thing.
        options.insert(i, tup)
        # push out the worst retained option.
        options.pop()

def find(chord, nmute = 0, important = 0, index = 1, nfrets = 12,
         # Below are ranking args (some are also used for finding)
         tuning = [], order = [], ranks = [], stringstarts = []):
    """
    This function is called in the main file, thatchord.py.
    
    In this function, all possible fret positions are considered on each string
    and are compiled into 'valids'. All positions which give any note
    in the chord are maintained. This has the disadvantage of considering, e.g.
    4 copies of C as a valid configuration for the chord C major.
    
    The second part of this function tests every possible configuration and
    calculates their ranks. It maintains a short list of the best options
    and then outputs the 'index'th best option found (default 0, i.e. best opt)
    To avoid recalculating ranks, options are stored as tuples.
    
    chord is a list of notes.
    
    tuning is a list of notes with as many entries as strings.
    
    nfrets is the number of frets of the instrument.
    
    important, if nonzero, is the number of notes from the requested chord that
    suffice to "define" the chord.
    """
    # define some basic variables. If 0 important notes, we assume the whole
    # chord is needed.
    n = len(tuning)
    valids = []
    if important == 0:
        important = len(chord)
    chordset = set(chord[:important])
    
    # start by finding all valid positions.
    for i in range(n):
        valids.append([])
        if i < nmute:
            valids[i].append(-1)
        for j in range(stringstarts[i], nfrets + 1):
            if (tuning[i] + j) % 12 in chord:
                valids[i].append(j)
    
    # we now have a list of possible frets for each string. Iterate through
    # each combination and filter out the ones that are not satisfactory.
    maxes = [len(l) for l in valids]
    
    # check we have valid options for each string
    if 0 in maxes:
        err(5)
    
    # all is good to go: initiate at first possibility and make list of valid
    # options.
    current = [0] * n
    options = []
    
    # populate list of note multiplicities. mults[i] is equal to the number of
    # distinct strings playing i.
    mults = [0] * 12
    for i in range(n):
        pass
    
    # want to iterate until we see 000..0 again
    first_value = [0] * n
    first_time  = True
    
    while first_time or current != first_value:
        first_time = False
        attempt = [valids[s][current[s]] for s in range(n)]
        
        # we will assess whether mutes are valid, and then whether sufficiently
        # many notes from the required chord have been hit.
        # First, see all muted strings. We already know they are < than nmute.
        
        muted = [i for i in range(n) if attempt[i] == -1]
        bool_mute = True
        if not len(muted) == 0:
            if not len(muted) == max(muted) + 1:
                bool_mute = False
        
        # Second, check that the attempt covers the important notes
        notes = [(attempt[i] + tuning[i]) % 12 for i in range(n) if attempt[i] != -1]
        bool_impo = len(set(chord[:important]) - set(notes)) == 0
        
        # if both conditions are satisfied, store the option.
        if bool_mute and bool_impo:
            r = rank.rank(attempt, chord, tuning, order, ranks, stringstarts)
            insert(options, attempt, index, r)
        
        # increment the current attempt to the next possibility.
        increment(maxes, current)
    
    # return the worst option in the list of options, which is at the index
    # requested (default is for options to have 1 entry).
    return options[-1][0]
