import random
from collections import defaultdict
import pprint as pp

STATEBIT = 2
TRANLEN = (2 ** (STATEBIT + 1)) * 2
HEADLEN = 5
TAILLEN = 5
assert HEADLEN == TAILLEN
MACHLEN = TRANLEN + HEADLEN + TAILLEN
TAPELEN = 9

def get_reading_frame(m, t):
    transition, head, tail, state = m
    ts = t #bin(t)[2:]
    cands = [ts[i:min(i+HEADLEN,TAPELEN)] + ts[:max(i+HEADLEN-TAPELEN,0)] for i in range(TAPELEN)]
    try:
        hi = cands.index(head)
    except:
        return -1, -1
    # hi = -1
    # for i, c in enumerate(cands):
    #     if head == c:
    #         hi = i
    #         break
    # if hi == -1:
    #     return -1, -1
    cands = cands[hi+1:] + cands[:hi+1]
    ti = -1
    for i, c in enumerate(cands):
        if tail == c:
            ti = (i+hi) % TAPELEN
            break
    if ti == -1:
        return -1, -1
    return hi, ti

def translate_tape(m, t, pm=0.0):
    hi, ti = get_reading_frame(m, t)
    if hi == -1:
        return False
    transition, head, tail, state = m
    ts = t # bin(t)[2:]
    ci = hi
    ts = list(ts)
    while True:
        c = int(ts[ci])
        ts[ci] = transition[2*state+c + TRANLEN//2]
        if random.random() < pm:
            ts[ci] = str(1 - int(ts[ci]))
        state = int(transition[2*state+c])
        ci += 1
        if ci == TAPELEN:
            ci = 0
        if ci == ti:
            break
    if all([c == '1' for c in ts]) or all([c == '0' for c in ts]):
        return False
    ts = ''.join(ts)
    return ts

def make_machine(t):
    n = TRANLEN + max(HEADLEN, TAILLEN)*2 // TAPELEN + 1
    tn = t * n
    translation = tn[0:(TRANLEN-1):2] + tn[1:TRANLEN:2]
    head = tn[TRANLEN:(TRANLEN+HEADLEN*2-1):2]
    tail = tn[(TRANLEN+1):(TRANLEN+TAILLEN*2):2]
    state = random.randint(0, 2**STATEBIT-1)
    return translation, head, tail, state

def initial_state(nm, nt):
    machines = [
        (
            ('{:0'+str(TRANLEN)+'b}').format(random.randint(0,2**TRANLEN-1)),
            ('{:0'+str(HEADLEN)+'b}').format(random.randint(0,2**HEADLEN-1)),
            ('{:0'+str(TAILLEN)+'b}').format(random.randint(0,2**TAILLEN-1)),
            random.randint(0, 2**STATEBIT-1)
        ) for i in range(nm)]
    tapes = [('{:0'+str(TAPELEN)+'b}').format(random.randint(0,2**TAPELEN-1)) for i in range(nt)]
    return machines, tapes

def calc_histogram(machines, tapes):
    mh = defaultdict(int)
    for m in machines:
        rep = hex(int(m[0]+m[1]+m[2], 2))[2:]
        mh[rep] += 1
    th = defaultdict(int)
    for t in tapes:
        rep = hex(int(t, 2))[2:]
        th[rep] += 1
    return mh, th

def print_histogram(mh, th):
    order_name = lambda x:int(x[0], 16)
    order_freq = lambda x:-x[1]
    ml = sorted([(m, f) for m, f in mh.items()], key=order_freq)
    print(ml)
    tl = sorted([(t, f) for t, f in th.items()], key=order_freq)
    print(tl)

nm, nt = 10, 3
capa_m, capa_t = 300, 300
pm = 0.08
stop_noise_gen = 100
generation = 1000
machines, tapes = initial_state(nm, nt)
print(0, calc_histogram(machines, tapes))
for g in range(1, generation):
    if g > stop_noise_gen:
        pm = 0
    new_machines, new_tapes = [], []
    for m in machines:
        for t in tapes:
            tmp = translate_tape(m, t, pm)
            if tmp != False:
                new_tapes.append(tmp)
            new_machines.append(make_machine(t))
    if len(new_machines) > capa_m:
        new_machines = random.choices(new_machines, k=capa_m)
    if len(new_tapes) > capa_t:
        new_tapes = random.choices(new_tapes, k=capa_t)    
    machines, tapes = new_machines, new_tapes
    print('g=', g, ', machines : ', len(machines), ', tapes : ', len(tapes))
    print_histogram(*calc_histogram(machines, tapes))
