exec(open('inspect_pcb.py').read().split('for i,e')[0])
for ix in [182,215,105]:
 x=data(entries[ix]);print(ix,repr(x[:120]));print(x[:250].hex())
