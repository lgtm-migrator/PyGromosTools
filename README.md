
![]()
![PyGromosBanLight](.img/PyGT_logo_dark_nobg_wide.png#gh-dark-mode-only)
![PyGromosBanLight](.img/PyGT_logo_light_nobg_wide.png#gh-light-mode-only)

Welcome to PyGromosTools
==============================

[//]: # (Badges)
[![CI](https://github.com/rinikerlab/PyGromosTools/actions/workflows/CI.yaml/badge.svg)](https://github.com/rinikerlab/PyGromosTools/actions/workflows/CI.yaml)
[![pre-commit](https://github.com/rinikerlab/PyGromosTools/actions/workflows/pre-commit.yml/badge.svg?branch=release3)](https://github.com/rinikerlab/PyGromosTools/actions/workflows/pre-commit.yml)
[![codecov](https://codecov.io/gh/rinikerlab/PyGromosTools/branch/main/graph/badge.svg?token=R36KJCEKEC)](https://codecov.io/gh/rinikerlab/PyGromosTools)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/rinikerlab/PyGromosTools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/rinikerlab/PyGromosTools/context:python)
[![DOI](https://zenodo.org/badge/323972251.svg)](https://zenodo.org/badge/latestdoi/323972251)
[![Documentation](https://img.shields.io/badge/Documentation-here-white.svg)](https://rinikerlab.github.io/PyGromosTools/)

Description
-------------

   The aim of the module is to bring GROMOS to the Python3 World!
   This repository should make it easier to work with GROMOS in Python and should enable the user to write cleaner, more reliable and adaptable code.

   General informations about functions can be found in our wiki and usage example for many general functions and theire relations are shown in jupyter notebooks in the examples in the example folder.

Content
-------------

* GROMOS wrappers
  * GromosXX wrapper: for simulation execution
  * GromosPP wrapper: for GROMOS++ program usage

* File handling of all GROMOS file types for automated creation/modification/analysis :
  * coordinate files CNF:
   * read and analyse CNF files
   * generate CNF files from RDKit
   * generate CNF files from SDF

    ```python
    cnf = Cnf(input_value="file_name")
    print(cnf.GENBOX)
    ```

  * topology files:
   * create topologies from a forcefield
    * GROMOS 2016H66 / 54A7
    * OpenForceField
    * SerenityForceField
   * modify topologies
    * add new atoms
    * modify force parameters

    ```python
    top = Top(input_value="file_path")
    top.add_new_SOLUTEATOM(ATNM=42)
    print(top)
    ```

  * simulation parameter files IMD
   * a wide option of templates provided
   * modify IMD files to fit your simulation

    ```pythons
    imd = Imd(input_value="file_path")
    imd.INITIALISE.TEMPI = 137
    print(imd)
    ```

  * trajectories (tre, trc, trg, ...)
   * analyse trajectories with Pandas data frames
   * standard analysis like RSMD, RDF, ... for trc
   * auto saving of results for later use as hdf5
   * ene_ana like tools for tre
   * easy to add costume analysis tools

    ```python
    trc = Trc(input_value="file_path")
    print(trc.rmsd().mean())
    ```

  * replica exchange files:
        repdat.dat
  * classes for single blocks of each of these files.

* Automation and file management system `gromos_system`
  * offers clean file management for simulations
  * offers a high level of automation
  * equiped with simulation queuing system
  * includes many force fields

  ```python
  ff=forcefield_system(name="openforcefield")
  gsys = Gromos_System(work_folder="dir", in_smiles="C1CCCCC1", auto_convert=True, Forcefield=ff)
  print(gsys)
  ```

* Simulation Submission and Execution :
  * Different Types of Simulation modules, like MD, SD or Emin.
  * Can be executed locally or on a cluster
  * easy to automatize and combine with analysis routines

  Run on a local machine:

  ```python
  from pygromos.files.gromos_system import Gromos_System
  from pygromos.simulations.hpc_queuing.submission_systems.local import LOCAL as subSystem
  from pygromos.simulations.modules.preset_simulation_modules import emin

  # define file paths (or use absolute file paths)
  root_dir = "./example_files/SD_Simulation"
  root_in_dir = root_dir+"/SD_input"
  cnf_path = root_in_dir+"/6J29_unitedatom_optimised_geometry.cnf"
  top_path = root_in_dir + "/6J29.top"
  sys_name = "6J29"

  # Build gromos System
  grom_system = Gromos_System(in_cnf_path=cnf_path, in_top_path=top_path,
                              system_name=sys_name, work_folder=root_in_dir)
  # Run Emin
  emin_gromos_system = emin(in_gromos_system=grom_system, submission_system=subSystem())

  ```

  Run on LSF-Cluster:
    ```python
  from pygromos.files.gromos_system import Gromos_System
  from pygromos.simulations.hpc_queuing.submission_systems.lsf import LSF as subSystem
  from pygromos.simulations.modules.preset_simulation_modules import emin

  # define file paths (or use absolute file paths)
  root_dir = "./example_files/SD_Simulation"
  root_in_dir = root_dir+"/SD_input"
  cnf_path = root_in_dir+"/6J29_unitedatom_optimised_geometry.cnf"
  top_path = root_in_dir + "/6J29.top"
  sys_name = "6J29"

  # Build gromos System:
  grom_system = Gromos_System(in_cnf_path=cnf_path, in_top_path=top_path,
                            system_name=sys_name, work_folder=root_in_dir)

  # Run Emin
  sub_system = subSystem(nmpi=4) # allows parallelization
  emin_gromos_system, jobID = emin(in_gromos_system=grom_system, submission_system=sub_system)

  ```

* Other utilities:
  * Bash wrappers for GROMOS
  * Amino acid library


Quick Setup
-------------

Quick Start - move to the root folder of this repository:
  ```bash
    # build environment
    conda env create -f conda_env.yaml
    conda develop -n pygromos ${PWD}

    # activate environment
    conda activate pygromos
  ```

In case the `conda develop` command does not work for you, you can also use `python -m pip install -e .` to install `PyGromosTools` in a development environment. Please make sure, that you have GROMOS (www.gromos.net) binaries around, if you want to use the MD-Package. We sadly can not provide the source code for this package, as it is currently not open-source.

If you find a bug or have an feature request, please raise an Issue on GitHub.

For more information, see INSTALL.md file for more informations.

Contributions
-------------

You want to contribute? Awesome! We are happy to support you in this process.
For any contribution, please check out the CODE_OF_CONDUCT.md file and the style guide in styleguide.md.
There will be a small code revision for code contributions, to verify that everything is in place.

Publications
-------------
Scientific Literature using PyGromosTools:
 * [RestraintMaker: a graph-based approach to select distance restraints in free-energy calculations with dual topology; Benjamin Ries^, Salomé Rieder^, Clemens Rhiner, Philippe H. Hünenberger and Sereina Riniker (2022). ](https://doi.org/10.1007/s10822-022-00445-6)
 * [Relative Free-Energy Calculations for Scaffold Hopping-Type Transformations with an Automated RE-EDS Sampling Procedure; Benjamin Ries, Karl Normak, R.Gregor Weiß, Salomé Rieder, Emília P. Barros, Candide Champion, Gerhard König, Sereina Riniker (2022)](https://link.springer.com/article/10.1007/s10822-021-00436-z)
 * [Modulation of the Passive Permeability of Semipeptidic Macrocycles: N- and C-Methylations Fine-Tune Conformation and Properties; Christian Comeau, Benjamin Ries, Thomas Stadelmann, et al. (2021)](https://pubmed.ncbi.nlm.nih.gov/33750117/)


^ contributed equally


Acknowledgements
----------------

Many thanks to Robin Wolf for the logo design!

Copyright
-------------

Copyright (c) 2020, Benjamin Ries, Marc Lehner, Salome Rieder, Felix Pultar, Paul Katzberger, Candide Champion

Project based on the
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.3.
