============
Requirements
============

In this section we discuss the following two use cases we have in mind for our 
distributed system: first a use case where the "life science" group in your 
organisation has performed a sequencing experiment, and you want to reliably 
store this data, the second use case being the bioinformatics group wanting to 
perform some analysis on this data.

Use Case 1: Store Datasets
==========================

Wether you collect the genomes of a large number of organisms, or just 
performed a new sequencing experiment, the data should be stored safely. The 
biological lab work is often done by a different group than the group 
performing the actual analysis on the data. The data coming from such 
experiment should be stored for later analysis.

This brings the following challenges:

* The huge amount of data: a human genome with 60x read coverage depth can 
  occupy easily 200 GB in its compressed FASTQ file format.
* The data needs to be stored persistently and reliably.
* The data needs to be accessible by other teams
* Analysis and other actions need to be performed on this dataset, and the 
  results should be stored too.

Use Case 2: perform analyses on the data
========================================

When the data is safely stored in the database, an organisation probably wants 
to analyse this data. Think of building a new phylogenetic tree based on a 
multiple sequence alignment of a collection of genomes. In the case of next 
generation sequencing you can think of mapping individual reads to a reference 
genome or locally align them, assemble a new genome from the individual reads, 
or check if this newly sequenced genome has any variant genes compared to the 
reference.

Most of these operations are computational expensive, but as discussed in the 
previous section, a lot of these operations can be performed in parallel, on 
smaller chunks of the data. Building a scalable distributed system for these 
kinds of pipelines could reduce the computational time significantly.

Requirements Prioritisation
===========================

For our system, we focus on computing the multiple sequence alignment of a 
large collection of genomes or protein sequences.

Must Have
---------

* Built a distributed system that computes the multiple sequence alignment of a
  large collection of genomes or protein sequences.
* The data must be stored consistently and reliably.
* Fault tolerant, when one of the nodes crashes it should not hinder the final 
  results. Able to resist one node down of any kind at the same time.
* Scalable, must be able to handle large genomes

Should have
-----------

* Let the user define a workflow, which specifies with steps to perform, and 
  which steps depends on which previous steps.
* Multi-tenancy: let multiple teams perform different actions simultaneously.

Could Have
----------

* Data-ownership: who can see which datasets
