
import sys
import time
import numpy as np
import random
import os
import datetime
from math import exp

top_filename='pboundary_top.zone'
bot_filename='pboundary_bottom.zone'
left_filename='pboundary_left_w.zone'
right_filename='pboundary_right_e.zone'
well_filename='well.zone'

os.system("sed -i '$d' pboundary_top.zone")
os.system("sed -i '$d' pboundary_bottom.zone")
os.system("sed -i '$d' pboundary_left_w.zone")
os.system("sed -i '$d' pboundary_right_e.zone")
os.system("sed -i '$d' pboundary_top.zone")
os.system("sed -i '$d' pboundary_bottom.zone")
os.system("sed -i '$d' pboundary_left_w.zone")
os.system("sed -i '$d' pboundary_right_e.zone")

with open (top_filename,'r') as f:
	first_line=f.readline()
        first_line=f.readline()
	first_line=f.readline()
	topn=int(f.readline())
	top_nodes=[map(int, line.split()) for line in f]

with open (bot_filename,'r') as f:
        first_line=f.readline()
        first_line=f.readline()
        first_line=f.readline()
        botn=int(f.readline())
        bot_nodes=[map(int, line.split()) for line in f]

with open (left_filename,'r') as f:
        first_line=f.readline()
        first_line=f.readline()
        first_line=f.readline()
        leftn=int(f.readline())
        left_nodes=[map(int, line.split()) for line in f]

with open (right_filename,'r') as f:
        first_line=f.readline()
        first_line=f.readline()
        first_line=f.readline()
        rightn=int(f.readline())
        right_nodes=[map(int, line.split()) for line in f]

siden = topn+botn+leftn+rightn

os.system("sed -i '$d' well.zone")
os.system("sed -i '$d' well.zone")

with open (well_filename,'r') as f:
        first_line=f.readline()
        first_line=f.readline()
        first_line=f.readline()
        welln=int(f.readline())
        well_nodes=[map(int, line.split()) for line in f]



fa= open('sideboundaries.zone','w')
fa.write("zone\n")
fa.write("000001    sizebound\n")
fa.write("nnum\n")
fa.write("      "+str(siden)+"\n")
for i in range(0, len(top_nodes)):
	for j in range (0, len(top_nodes[i])):
		node=top_nodes[i][j]
		fa.write("   "+str(node));

	fa.write("\n")

for i in range(0, len(bot_nodes)):
        for j in range (0, len(bot_nodes[i])):
                node=bot_nodes[i][j]
                fa.write("   "+str(node));

        fa.write("\n")

for i in range(0, len(left_nodes)):
        for j in range (0, len(left_nodes[i])):
                node=left_nodes[i][j]
                fa.write("   "+str(node));

        fa.write("\n")

for i in range(0, len(right_nodes)):
        for j in range (0, len(right_nodes[i])):
                node=right_nodes[i][j]
                fa.write("   "+str(node));

        fa.write("\n")

fa.write("000002   well\n")
fa.write("nnum\n")
fa.write("      "+str(welln)+"\n")
for i in range(0, len(well_nodes)):
        for j in range (0, len(well_nodes[i])):
                node=well_nodes[i][j]
                fa.write("   "+str(node));

        fa.write("\n")



fa.write("\n")
fa.write("stop \n")

fa.close()
print "Done"


