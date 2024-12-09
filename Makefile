.PHONY: C_stor_correct C_uge_correct DFN_Mesh_Connectivity_Test DFNGen DFNTrans all clean

all: C_stor_correct C_uge_correct DFN_Mesh_Connectivity_Test DFNGen DFNTrans

C_stor_correct:
	$(MAKE) -C C_stor_correct

C_uge_correct:
	$(MAKE) -C C_uge_correct

DFN_Mesh_Connectivity_Test:
	$(MAKE) -C DFN_Mesh_Connectivity_Test

DFNGen:
	$(MAKE) -C DFNGen

DFNTrans:
	$(MAKE) -C DFNTrans

install: all
	mkdir -p pydfnworks/pydfnworks/bin
	cp C_stor_correct/correct_stor pydfnworks/bin
	cp C_uge_correct/correct_uge pydfnworks/bin
	cp DFN_Mesh_Connectivity_Test/ConnectivityTest pydfnworks/bin
	cp DFNGen/DFNGen pydfnworks/bin
	cp DFNTrans/DFNTrans pydfnworks/bin

clean:
	$(MAKE) -C C_stor_correct clean
	$(MAKE) -C C_uge_correct clean
	$(MAKE) -C DFN_Mesh_Connectivity_Test clean
	$(MAKE) -C DFNGen clean
	$(MAKE) -C DFNTrans clean
	rm pydfnworks/bin/correct_stor
	rm pydfnworks/bin/correct_uge
	rm pydfnworks/bin/ConnectivityTest
	rm pydfnworks/bin/DFNGen
	rm pydfnworks/bin/DFNTrans
