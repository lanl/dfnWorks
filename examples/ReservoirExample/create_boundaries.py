import numpy as np


def read_in_nodes(filename):
    with open (filename,'r') as f:
        #ignore header
        first_line=f.readline()
        first_line=f.readline()
        first_line=f.readline()
        # get number of nodes
        number_of_nodes=int(f.readline())
        nodes=np.zeros(number_of_nodes)
        i = 0
        for line in f.readlines():
            for value in line.split():
                nodes[i]=value
                i+=1
                if i == number_of_nodes:
                    return nodes

print("--> Merging Zone Files")
top_filename='pboundary_top.zone'
bottom_filename='pboundary_bottom.zone'
left_filename='pboundary_left_w.zone'
right_filename='pboundary_right_e.zone'
well_filename='well.zone'

top_nodes=read_in_nodes(top_filename)
bottom_nodes=read_in_nodes(bottom_filename)
left_nodes=read_in_nodes(left_filename)
right_nodes=read_in_nodes(right_filename)

nodes=np.concatenate((top_nodes,bottom_nodes,left_nodes,right_nodes)) 

well_nodes=read_in_nodes(well_filename)

fa= open('sideboundaries.zone','w')
fa.write("zone\n")
fa.write("000001    sizebound\n")
fa.write("nnum\n")
fa.write("      "+str(len(nodes))+"\n")

cnt=0
for i in range(len(nodes)):
    fa.write("      %d"%nodes[i]);
    cnt+=1
    if cnt == 9:
        fa.write("\n")
        cnt=0
fa.write("\n")
fa.write("000002   well\n")
fa.write("nnum\n")
fa.write("      "+str(len(well_nodes))+"\n")
cnt=0
for i in range(len(well_nodes)):
    fa.write("      %d"%well_nodes[i]);
    cnt+=1
    if cnt == 9:
        fa.write("\n")
        cnt=0

fa.write("\n\n")
fa.write("stop \n")

fa.close()
print("--> Merging Zone Files Complete")
      

