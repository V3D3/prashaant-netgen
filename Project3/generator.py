def requirefile(file):
    try:
        f = open(file)
        out = f.read()
        f.close()
        return out
    except OSError:
        print('Failed to open ' + f)
        exit()

requirefile('core.bsv')
L1T = requirefile('L1Topology.txt')
L2T = requirefile('L2Topology.txt')