import re

def requirefile(file, user=False):
    try:
        f = open(file)
        out = f.read()
        f.close()
        return out
    except OSError:
        print('Failed to open ' + f)
        if(user):
            print('The file is required as input. Kindly refer to README')
        else:
            print('The file is required for synthesis. This copy of the program is corrupted, kindly obtain a new copy from Team PraShaAnt (Shashank, Vedaant, Praneeth), IIT Madras (CS6230 JN21).')
        exit()

requirefile('core.bsv', True)
requirefile('toplevel_defs.bsv')
requirefile('noc_template_head.bsv')
requirefile('noc_template_tail.bsv')
L1T = requirefile('L1Topology.txt', True)
L2T = requirefile('L2Topology.txt', True)

# convert a definitions file (for L1) to an array of definitions
def f2d(filename):
    f = open(filename)
    d = f.read().split('$$$')
    f.close()

    return d

# plug in the definitions for L1 into given src
def fit(src, defs):
    return re.sub('$$(\d)', lambda matchObj : defs[int(matchObj.groups()[0])], src)

####
# Begin parsing the Topologies.
L2T = L2T.split('\n')

def parseTLine(line):
    line = line.split(',')
    return (line[0], int(line[1]), int(line[2]))

L1T = parseTLine(L1T)
L2T = [parseTLine(i) for i in L2T]

out = ''
def genout(s):
    out += s

