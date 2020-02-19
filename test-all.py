#!/usr/bin/env python3

# TODO: ASUM FAILS

import subprocess
from datetime import datetime

def average(values):
    if len(values):
        return sum(values) / len(values)
    else:
        return 0

def parse(output):
    data = []
    benchmark = None
    for l in output.split('\n'):
        l = l.strip()
        if l.startswith('---'):
            benchmark = l.split(' ')[1]
            data.append((benchmark, []))
        elif 'PASS' in l:
            assert benchmark
            tokens = [x for x in l.split(' ') if x]
            data[-1][1].append(float(tokens[-3]))
    return data

levels = list(range(1, 4))
types = ['s', 'd', 'c', 'z']
runs = 5

workloads = [2**26, 2**13, 2**11]

results = {}

total = len(levels) * len(types)
i = 0
for level in levels:
    for t in types:
        i += 1
        binary = 'x%sl%dblastst' % (t, level)
        workload = workloads[level - 1]
        if t == 'z':
            workload /= 2
        elif t == 'c' and level == 3:
            workload /= 2
        cmd = 'taskset 0x1 ./bin/%s -R all -N %d %d 1' % (binary, workload, workload)
        if level <= 2:
            cmd += ' -X %d %s' % (runs, ' '.join(['1'] * runs))
        else:
            args = '1'
            if t == 'c' or t == 'z':
                args = '1 1'
            cmd += ' -a %d %s' % (runs, ' '.join([args] * runs))
        print('%d/%d: %s' % (i, total, cmd))
        start = datetime.now()
        r = subprocess.check_output(cmd, shell = True, stderr = subprocess.DEVNULL, encoding = 'utf8')
        end = datetime.now()
        duration = (end - start).total_seconds()
        print('Took: %.2f s' % duration)
        data = parse(r)
        results[(t, level)] = [data, workload]

with open('openblas.csv', 'w+') as f:
    f.write('type;benchmark;N;mflops\n')
    for level in levels:
        for t in types:
            data = results[(t, level)]
            workload = data[1]
            for d in data[0]:
                key = d[0]
                values = d[1]
                f.write('%s%d;%s;%d;%.2f\n' % (t.upper(), level, key, workload, average(values)))
