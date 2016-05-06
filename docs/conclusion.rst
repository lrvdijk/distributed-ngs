.. _section-conclusion:

==========
Conclusion
==========

This report discusses the design of a distributed system for running 
bioinformatics software. In this report we focus on running MAFFT in a 
distributed manner. The system has three different nodes: manager nodes, data 
nodes and computational worker nodes, which means our system has both a simple 
distributed file system and a computational grid.

Our system is fault tolerant: the system is guaranteed to function correctly 
when at most one node of each kind is down. Running an experiment with a real 
world dataset on Google Compute Engine showed a significant decrease in runtime 
with more nodes, but more experiments are needed to properly see the overhead 
effects of the data transfer between worker, data and manager nodes.

The system also easily scales, and it is almost no effort to add another worker
or data node. One concern could be the managers: they need to replicate and 
share the metadata stored in a PostgreSQL databases and the queues in the 
RabbitMQ server. We think this will not become an issue quickly because the 
write operations are small and quick, and more than three managers is not 
likely to happen. The slowdown due to replication will therefore probably be
small.

All our must-have requirements have therefore been met.
