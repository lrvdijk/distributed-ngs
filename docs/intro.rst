============
Introduction
============

In the past few years sequencing the genome has become a lot cheaper, due to
next generation sequencing techniques. It is now a lot more viable to sequence
the genome of an organism, and for example compare it to a known reference
genome. The human genome consists of three billion base pairs, and some plant
genomes are sometimes an order of magnitude larger. 

This data avalanche provides a lot of opportunities for biological problems. 
But the amount of data is huge and a lot of operations are computationally 
expensive. Luckily, these operations are often quite easily executed in 
parallel. A few examples are discussed in the following sections.

Next Generation Sequencing
==========================

A typical NGS pipeline consists of the following steps:

1. A genome sequencing machine produces a lot of independent short reads 
   (around 200 base pair) originating from random locations of a new genome.
2. Try to map these reads to a known reference genome
3. Determine variant genes in the newly sequenced genome

These short reads can be independently mapped to a reference genome, which 
makes it easy to distribute these reads across multiple workers. Decap et al. 
built a distributed system based on Hadoop [decap2015halvade]_.

Multiple Sequence Alignment/Phylogeny
=====================================

If you have a lot of genome or protein sequences, you can try to match each 
sequence to each other, a process called alignment. If you have a collection of
aligned sequences, you can calculate the distance between each combination of 
sequences, and from there you can generate a phylogenetic tree. 

This process of multiple sequence alignment and distance calculation can also 
be quite easily performed in parallel, although it requires a merge step at the
end.

A Distributed System For Bioinformatics
=======================================

We would like to design a system which can run bioinformatics software easily 
on multiple workers. To bound our project a bit, we will focus on the multiple 
sequence alignment problem. 

.. [decap2015halvade] 
   Decap, D., Reumers, J., Herzeel, C., Costanza, P., & Fostier, J. (2015). Halvade: scalable sequence analysis with MapReduce. *Bioinformatics*, 31(15), 2482-2488.
