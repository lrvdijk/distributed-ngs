.. _section-experiments:

===========
Experiments
===========
We have tested our system using MAFFT. MAFFT is a simple tool for doing multiple sequence alignments
for both amino acids and nucleotides. We have chosen this tool because of it simplicity in use and
for the simplicity of parallelizing multiple sequence alignments.
For the data sequences we data available from the Universal Protein Resource (uniprot). Uniprot is a
collaboration between different institution providing annotated protein sequences. We are using the
Reviewed (Swiss-Prot) dataset that consists of annotated and reviewed sequences. The size of is roughly
253MB, and consists of 550960 different sequences. To also test larger files we have duplicated the content
multiple times into new files to create files with sizes of: 506MB, 1012MB and 2024MB.

Timing is done based on the time when MAFFT jobs enter the rabbit queue until the queue is empty again.
This removes the time for calculating the offsets, which is calculated on the data node. However the time to
transfer the data chunks from datanodes to computational nodes is part of the timing. This allows us to still detect
possible bottlenecks in the data transfers.


Scalability
===========

Fault tolerance
===============



