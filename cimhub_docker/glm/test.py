import os
import glm
import json
import subprocess as sub
from pprint import pprint as pp

p = open('z.glm', 'w')
with open ('master_run.glm') as f:
    content = f.readlines()
    for lines in content:
        x = lines.strip()
        if (x.startswith('starttime')) or (x.startswith('stoptime')) :
            x = x.split(' ')
            if x[0] == 'starttime':
                x[1] = "starttime '2000-01-01 0:00:00';"
                x = x[1]
            if x[0] == 'stoptime':
                x[1] = "stoptime '2000-01-01 0:00:00';"
                x = x[1]
        if x.startswith('#include'):
            x = x.split(' ')
            x[1] = '#include "master_base.glm";'
            x = x[1]
        if not (x.endswith('{')) and not (x.startswith('}')) and not (x.startswith('#')) and not (x.startswith('};')) and not (x.startswith('module')):
            print(' ' * 4 + x, file=p)
        else:
            print(x, file=p)
