# SimFrac

pySimFrac is a Python-based library for constructing 3D single fracture geometries. The software is designed to help researchers and practitioners to investigate flow through fractures through direct numerical simulations of single/multi phase flow through fractures. One advantage of the Python implementation is that it allows for greater flexibility and customization compared to a GUI-based approach. With a Python-based interface, researchers can more easily expand the development and test new fracture generation algorithms or modify existing methods to better match experimental data. pySimFrac offers a spectral-based and convolution-based methods. 
pySimFrac also includes utilities for characterizing fracture properties such as the correlation length, moments, and probability density function of the fracture surfaces and aperture field. 

## Install
To install pySimFrac, use the following commands 

```bash
git clone https://github.com/lanl/dfnWorks
git checkout pysimfrac
cd pysimfrac/src/
# install module 
python setup.py install --user  
```


