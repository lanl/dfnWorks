.. _simfrac-effective-aperture:

Effective Apertutre 
========================================

Estimations of the effective properties from the structure of the surfaces are also provided by simfrac. These estimations are categorized into two types. The first are analytical and empirically derived estimations of the effective hydraulic aperture and the second are numerical approximations.  The first estimations includes standard approximations such as various means, e.g., arithmetic, harmonic, and geometric, as well as several models proposed in the literature. Most of the models proposed in the literature use moments of the aperture distribution, which can be directly computed using the analysis toolkit. In principle, any effective hydraulic model with geo-statistical parameters can be added to simfrac. The second type of approximations are obtained by numerical inversion of the Darcy equation with a spatially variable permeability field inferred using a local cubic law from the aperture field. Note, that other functional relationships between aperture and permeability can be readily applied as well.  We obtain pressure and volumetric flow rates by solving the standard flow equations with variable coefficients discretized using a second-order finite scheme.  Flow is driven by Dirchelet pressure boundary conditions in one primary direction to obtain estimates of effective permeability in that direction, which is then converted to an effective hydraulic aperture. 


Estimate Effective Aperture 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pysimfrac.src.analysis.effective_aperture.effective_aperture 
        :members: get_effective_aperture
        :noindex:
        
Example: 

.. code-block:: python

        # make fracture
        myfrac = SurFrac(h = 0.01, lx = 3, ly = 1, 
                        method = "spectral",
                        units = 'mm')
        myfrac.params["H"]["value"] = 0.5
        myfrac.params["roughness"]["value"] = 0.05
        myfrac.params["aniso"]["value"] = 0.5
        myfrac.params["mismatch"]["value"] = 0.1
        myfrac.params["model"]["value"] = "smooth"
        myfrac.create_fracture()

        ## estimate effective aperture 
        myfrac.get_effective_aperture('gmean')
        myfrac.get_effective_aperture('mean')
        myfrac.get_effective_aperture('hmean')
        myfrac.get_effective_aperture('numerical')
        print(myfrac.effective_aperture)

