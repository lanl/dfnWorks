
Instructions for running DFNGen verification and validation tests:

1.  Navegate to the DFNGen soucre code folder. 
    Open testing.h and uncomment what is there.
        
    testing.h should contain: 
        #ifndef TESTING
        #define TESTING
        #endif

        #ifndef DISABLESHORTENINGINT
        #define DISABLESHORTENINGINT
        #endif 
   

2.  Recompile the DFNGen source code.
    Navigate to source folder in terminal

    Enter command: 'make clean && make'


3.  Run the python script "testDFN.py". (ex: "python2.7 testDFN.py")
    File should be in the same directory as this README file


4. Observe output, all tests should output "Test passed". Any tests which 
   ouput "TEST FAILED" must be debugged. 

    Debug Tips:
        Enable full mesh by setting "visualizationMode: 0" in the tests corresponding 
        python script.

        View the programOutput.txt file in the corresponding tests output folder.
    

5.  Navegate back to the DFNGen source code folder 
    Open testing.h and COMMENT EVERYTHING in the file.


6.  Run the python script "Run_Shorten_Intersection_Tests.py".
    (ex: "python2.7 Run_Shorten_Intersection_Tests.py)
    File should be in the same directory as this README file


7.  The output for the "Run_Shorten_Intersection_Tests.py" scipt must be manually
    verified by examining the produced meshes in the output folders. 

    These tests test the capability of the shortening intersection algorithm. 
    Intersections are shotened (if necessary) to preserve mesh quality and 
    to increase the fracture acceptance rate.     
