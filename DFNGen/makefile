CXX = g++ 
CXXFLAGS  = -std=c++11 -O3 -lm -Wall -g

# Automatic dependency generation: -MMD emits a .d file alongside each .o
# that lists the exact headers that .cpp included. -MP adds phony targets
# for headers so a deleted header doesn't cause a spurious error.
DEPFLAGS = -MMD -MP

OBJS = DFNmain.o debugFunctions.o distributions.o expDist.o hotkey.o \
       readInput.o readInputFunctions.o output.o insertUserRects.o \
       insertUserRectsByCoord.o insertUserEllByCoord.o insertUserEll.o \
       insertUserPolygonByCoord.o insertShape.o structures.o \
       computationalGeometry.o fractureEstimating.o generatingPoints.o \
       domain.o layers.o mathFunctions.o polygonBoundary.o vectorFunctions.o \
       removeFractures.o clusterGroups.o

# Pull in auto-generated dependency files (silently ignore if not yet built)
-include $(OBJS:.o=.d)

DFNGen: $(OBJS)
	$(CXX) $(CXXFLAGS) -o DFNGen $(OBJS)

# Single pattern rule covers all translation units.
# $< is the .cpp file; DEPFLAGS writes the .d file as a side effect.
%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(DEPFLAGS) -c -o $@ $<

clean:
	rm -f DFNGen $(OBJS) $(OBJS:.o=.d)