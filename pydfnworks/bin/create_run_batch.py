#
#fp = open("run_batch_uniform.sh", "wb")
#weights = weights = ['indicator', 'perm', 'length', 'permlength']
#cmd = "python run_prune_explicit.py -name /lclscratch/jhyman/5m-cube/var_0.5_x%02d/bb_%s -prune_path /lclscratch/jhyman/5m-cube/var_0.5_x%02d/ -prune_file = /lclscratch/jhyman/5m-cube/var_0.5_x%02d/bb_%s.dat -input run_file.txt -ncpu 64\n"
#for i in range(1,31):
#    for w in weights:
#        fp.write(cmd%(i,w,i,i,w))
#
#cmd = "python run_prune_explicit.py -name /lclscratch/jhyman/5m-cube/var_1.0_x%02d/bb_%s -prune_path /lclscratch/jhyman/5m-cube/var_1.0_x%02d/ -prune_file = /lclscratch/jhyman/5m-cube/var_1.0_x%02d/bb_%s.dat -input run_file.txt -ncpu 64\n"
#for i in range(1,31):
#    for w in weights:
#        fp.write(cmd%(i,w,i,i,w))
#
#cmd = "python run_prune_explicit.py -name /lclscratch/jhyman/5m-cube/var_1.5_x%02d/bb_%s -prune_path /lclscratch/jhyman/5m-cube/var_1.5_x%02d/ -prune_file = /lclscratch/jhyman/5m-cube/var_1.5_x%02d/bb_%s.dat -input run_file.txt -ncpu 64\n"
#for i in range(1,31):
#    for w in weights:
#        fp.write(cmd%(i,w,i,i,w))
#fp.close()
#
#
fp = open("run_batch_uniform.sh", "wb")
cmd = "python run_explicit.py -name /lclscratch/jhyman/5m-cube/var_1.5_x%02d -path /lclscratch/jhyman/5m-cube/ -input run_file.txt -ncpu 64\n"
for i in range(1,31):
    fp.write(cmd%(i))
fp.close()
#




exit()

fp = open("run_batch_backbone.sh", "w")
#cmd = 'python run_prune_explicit.py -name /lclscratch/jhyman/x%02d/disjoint_%s -prune_file /project/bes_dfn/jhyman/dfn2graph_networks/backbone_x%02d/disjoint_%s.dat -prune_path /project/bes_dfn/jhyman/dfn2graph_networks/backbone_x%02d/ -ncpu 32 -input run_file.txt\n'
#weights = ['indicator', 'perm', 'length', 'permlength']
#for w in weights:
#    for i in range(11,100):
#        fp.write(cmd%(i,w,i,w,i))
#fp.close()
#fp = open("run_batch_uniform.sh", "w")
#cmd = 'python run_prune_explicit.py -name /lclscratch/jhyman/5m-cube/var_0/disjoint_%s -prune_file /lclscratch/jhyman/5m-cube/var_0/disjoint_%s.dat -prune_path /lclscratch/jhyman/5m-cube/var_0/ -ncpu 32 -input run_file.txt\n'
#weights = ['indicator', 'perm', 'length', 'permlength']
#for w in weights:
#    fp.write(cmd%(w,w))
#cmd = 'python run_prune_explicit.py -name /lclscratch/jhyman/5m-cube/var_0.5/disjoint_%s -prune_file /lclscratch/jhyman/5m-cube/var_0.5/disjoint_%s.dat -prune_path /lclscratch/jhyman/5m-cube/var_0.5/ -ncpu 32 -input run_file.txt\n'
#weights = ['indicator', 'perm', 'length', 'permlength']
#for w in weights:
#    fp.write(cmd%(w,w))
#cmd = 'python run_prune_explicit.py -name /lclscratch/jhyman/5m-cube/var_1/disjoint_%s -prune_file /lclscratch/jhyman/5m-cube/var_1/disjoint_%s.dat -prune_path /lclscratch/jhyman/5m-cube/var_1/ -ncpu 32 -input run_file.txt\n'
#weights = ['indicator', 'perm', 'length', 'permlength']
#for w in weights:
#    fp.write(cmd%(w,w))
#cmd = 'python run_prune_explicit.py -name /lclscratch/jhyman/5m-cube/var_1.5/disjoint_%s -prune_file /lclscratch/jhyman/5m-cube/var_1.5/disjoint_%s.dat -prune_path /lclscratch/jhyman/5m-cube/var_1.5/ -ncpu 32 -input run_file.txt\n'
#weights = ['indicator', 'perm', 'length', 'permlength']
#for w in weights:
#    fp.write(cmd%(w,w))
#fp.close()
