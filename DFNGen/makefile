 CXX = /opt/homebrew/Cellar/gcc/11.3.0_2/bin/g++-11
CXXFLAGS  = -std=c++11 -O3 -lm -Wall -g

DFNGen: DFNmain.o debugFunctions.o distributions.o expDist.o hotkey.o  readInput.o readInputFunctions.o output.o insertUserRects.o insertUserRectsByCoord.o insertUserEllByCoord.o insertUserEll.o insertUserPolygonByCoord.o insertShape.o structures.o computationalGeometry.o fractureEstimating.o generatingPoints.o domain.o mathFunctions.o polygonBoundary.o vectorFunctions.o generatingPoints.o removeFractures.o  clusterGroups.o
	
	$(CXX) $(CXXFLAGS) -o DFNGen DFNmain.o debugFunctions.o distributions.o expDist.o fractureEstimating.o  hotkey.o readInput.o readInputFunctions.o output.o insertUserRects.o insertUserRectsByCoord.o insertUserEllByCoord.o  insertUserEll.o insertUserPolygonByCoord.o insertShape.o structures.o computationalGeometry.o  domain.o mathFunctions.o vectorFunctions.o generatingPoints.o removeFractures.o clusterGroups.o polygonBoundary.o


DFNmain.o:  DFNmain.cpp  input.h 

hotkey.o: hotkey.cpp hotkey.h

readInput.o: readInput.cpp input.h

readInputFunctions.o: readInputFunctions.cpp readInputFunctions.h input.h

output.o: output.cpp output.h

structures.o: structures.cpp structures.h

insertUserRects.o: insertUserRects.cpp insertShape.h   

insertUserRectsByCoord.o: insertUserRectsByCoord.cpp insertShape.h

insertUserEllByCoord.o: insertUserEllByCoord.cpp insertShape.h

insertUserEll.o: insertUserEll.cpp insertShape.h

insertUserPolygonByCoord.o: insertUserPolygonByCoord.cpp insertShape.h

insertShape.o: insertShape.cpp insertShape.h

vectorFunctions.o: vectorFunctions.cpp vectorFunctions.h 

computationalGeometry.o: computationalGeometry.cpp computationalGeometry.h

generatingPoints.o: generatingPoints.cpp generatingPoints.h

domain.o: domain.cpp domain.h

mathFunctions.o: mathFunctions.cpp mathFunctions.h

clusterGroups.o: clusterGroups.cpp clusterGroups.h

distributions.o: distributions.cpp distributions.h

expDist.o: expDist.cpp expDist.h

fractureEstimating.o: fractureEstimating.cpp fractureEstimating.h

debugFunctions.o: debugFunctions.cpp debugFunctions.h

removeFractures.o: removeFractures.cpp removeFractures.h

polygonBoundary.o: polygonBoundary.cpp polygonBoundary.h 

clean:
	rm -f DFNGen DFNmain.o debugFunctions.o  distributions.o expDist.o fractureEstimating.o hotkey.o structures.o insertUserEll.o insertUserPolygonByCoord.o insertUserRects.o insertUserRectsByCoord.o computationalGeometry.o output.o readInput.o readInputFunctions.o mathFunctions.o vectorFunctions.o generatingPoints.o domain.o clusterGroups.o insertShape.o removeFractures.o insertUserEllByCoord.o polygonBoundary.o

