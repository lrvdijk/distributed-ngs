.. _section-discussion:

==========
Discussion
==========

We have built a quite complex distributed system:

* A simple distributed file system for storing datasets
* A computational grid for running bioinformatics software
* A custom communication protocol between all nodes

The size of this project plus a few uncertainties at the beginning of this
project (what will be our project exactly? Focus on which bioinformatics software
package?) are a few reasons this project took a bit more time than expected. As
a result we unfortunately could not do all experiments we would have wanted to
do.

Scalability
===========

We think our system scales well: it's easy to add a new data node or
computational node. Data nodes need to register with the manager, computational
nodes do not need to do anything: just pick a subtask from the job queue. 

One concern for the scalability could be the consistency management of all
managers, the data needs to be replicated on each manager. We do not think this 
will become an issue very quickly, because most actions on the manager are read
operations (where is this dataset located?), and if there is a write operation,
it is often a small one (only metadata). Furthermore, we think it is not likely
that one would need more than three managers, and therefore the replication
slowdown is probably relatively small. This should be confirmed with further
experiments.

Performance
===========

As seen in the real world experiment the performance is quite good. With
multiple workers a large multiple sequence alignment is only a matter of
minutes. There are however a few concerns: the preprocessing step can take
a lot of time, and although the resulting byte offsets can be cached, this is
not really convenient.

Furthermore, we would like to recommend more experiments with more workers and
multiple managers. More workers means more result datasets written to the data
nodes (and the manager for metadata), which could hurt the performance a bit,
especially when you have multiple managers (and therefore the required
replication).

Fault Tolerance
===============

We think our system meets our fault tolerance requirements quite well. We
ensure there is no single point of failure, and the system can handle one node
down of each kind at the same time. Furthermore, when a worker dies while
processing a subtask, this subtask is automatically requeued. This indirectly
moves this task eventually to another available worker. 

Some improvements could be adding error correcting codes to each dataset, to
fix the data in case of a partial harddisk failure.
