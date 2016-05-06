============
Introduction
============

In the past few years sequencing the genome has become a lot cheaper, due to
next generation sequencing techniques. It is now a lot more viable to sequence
the genome of a patient, and for example compare it to a known reference
genome. The human genome consists of three billion base pairs, and some plant
genomes are sometimes an order of magnitude larger. So we are dealing with a
huge amount of data, and the algorithms for mapping short reads on the
reference genome, alignment, or de novo genome assembly can be quite
computationally heavy. Furthermore, if you have mapped your reads to a
reference genome, you will probably want to perform several kinds of analysis
on your newly sequenced genome, for example check if there are any genes
different compared to the reference.

Because you retrieve a lot of individual short reads from your sequencing step,
you can map and align these reads independently to a reference genome. Leading to
a lot of possibilities for parallelization. The idea is to
build a distributed system to handle this next generation
sequencing pipeline, to perform some of this assembly and mapping algorithms in
parallel, distributed over a set of "computational super nodes". This also
brings the challenge to efficiently manage the corresponding datasets.
Decap et al. already built a similar system using Hadoop [decap2015halvade]_.

In this assignment we will focus on the distributed system, and initially only
implement a subset of the steps instead of the whole NGS pipeline.

.. [decap2015halvade] 
   Decap, D., Reumers, J., Herzeel, C., Costanza, P., & Fostier, J. (2015). Halvade: scalable sequence analysis with MapReduce. *Bioinformatics*, 31(15), 2482-2488.
