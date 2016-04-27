============
Requirements
============

In this section we discuss the following two use cases we have in mind for our 
distributed system: first a use case where the "life science" group in your 
organisation has performed a sequencing experiment, and you want to reliably 
store this data, the second use case being the bioinformatics group wanting to 
perform some analysis on this data.

Use Case 1: store the data of a sequencing experiment
-----------------------------------------------------

The biological lab work is often done by a different group than the group  
performing the actual analysis on the data. Although the costs of sequencing 
have dropped dramatically recently, it's still relatively expensive ($1000 
dollar per experiment). The data coming from such experiment should be stored 
for later analysis.

This brings the following challenges:

* The huge amount of data: a human genome with 60x read coverage depth can 
  occupy easily 200 GB in its compressed FASTQ file format.
* The data needs to be stored persistently and reliably.
* The data needs to be accessible by other teams
* Analysis and other actions need to be performed on this dataset, and the 
  results should be stored too.

Use Case 2: perform analyses on the data
----------------------------------------

When the data is safely stored in the database, an organisation probably wants 
to analyse this data. For example, map individual reads to a reference genome 
or locally align them, assemble a new genome from the individual reads, or 
check if this newly sequenced genome has any variant genes compared to the 
reference.

Most of these operations can take a lot of time, but due to the nature of the 
sequencing experiment (you get a lot of independent reads), it is possible to 
perform a lot of steps at the same time, but on different chunks of the data. 
Building a scalable distributed system for these kinds of pipelines could 
reduce the computational time significantly.

Requirements Prioritisation
---------------------------

Must Have
^^^^^^^^^

* Built a distributed system which implements a subset of the steps of a NGS 
  pipeline: Burrows-Wheeler alignment and local alignment on independent reads, 
  keeping the known best practices in mind [auwera2013fastq]_.
* The data must be stored consistently and reliably.
* Fault tolerant, when one of the nodes crashes it should not hinder the final 
  results. Able to resist one node down of any kind at the same time.
* Scalable, must be able to handle large genomes

Should have
^^^^^^^^^^^

* Different scheduling policies for different workloads
* Multi-tenancy: let multiple teams perform different actions simultaneously.

Could Have
^^^^^^^^^^

* Data-ownership: who can see which datasets

.. [auwera2013fastq] 
    Auwera, G. A., Carneiro, M. O., Hartl, C., Poplin, R., del Angel, G., 
    Levy‐Moonshine, A., ... and Banks, E. (2013). From FastQ data to 
    high‐confidence variant calls: the genome analysis toolkit best practices 
    pipeline. *Current Protocols in Bioinformatics*, 11-10.
