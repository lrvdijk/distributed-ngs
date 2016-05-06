.. _section-system-design:

=============
System Design
=============

The general idea is to have a multi cluster architecture with centralized 
scheduling. There are three kind of nodes:

* Central manager nodes
* Data nodes
* Computational worker nodes

An overview of the system can be seen in :numref:`fig-overview`.

.. _fig-overview:

.. figure:: img/overview.png
    :scale: 50 %

    Global system overview

Central Managers
================

The central managers are the most intelligent nodes of the system and 
coordinate the whole system. Central managers keep track which datasets are 
stored on which data nodes, and handle the requests for certain analyses
on a dataset. They also take care of splitting a task into multiple subtasks, 
which can be distributed across workers.

Central managers store a lot of metadata, and the idea is to replicate this 
data on all central managers. This data is stored in a PostgreSQL database, and
using pgPool-II [pgpool]_ it is possible to setup the replication system. The 
persistent messaging middleware also runs on the central manager, and in our 
case we use RabbitMQ [rabbitmq]_ as our message queue. RabbitMQ has built in 
functionality to share message queues across multiple nodes, and keep those 
queues consistent. 

We assume all nodes will be located in the same data center (it is a 
distributed system for a single company or research group), and therefore the 
chance of a network partition is considered low.

Data Nodes
==========

All datasets are stored on dedicated "data nodes". To prevent any data loss, 
and to retain high availability/access of the data, the central manager makes sure
that each dataset is stored on multiple different nodes. Clients communicate with
the central manager about where to store initial new data, however the transfer is
done directly from client to data node to not unnecessary increase data 
transfers. We specified in our fault tolerant requirements that the system 
should be tolerant to at most one unavailable node of each type, and thus each 
dataset is stored on two data nodes.

Data nodes are a simple distributed file system, but they also provides some 
more intelligent functionality. They can calculate proper byte offsets to split
a file into multiple chunks for a limited set of file types. We do this 
calculation on the data node, because otherwise you would need to transfer the 
possibly large dataset to another node.

Computational Worker Nodes
==========================

The worker nodes are the power horses in our system: they perform the actual 
computationally intensive operations on datasets. The central managers build a 
queue with tasks waiting to be run, and these worker nodes can pick one this 
queue. 

Each task in the queue contains the metadata which program to run and on which 
dataset (and optionally a chunk start and end byte offset). When a worker node 
picks a task, it asks the central manager which data node it should contact to 
retrieve the data, and continues to download that dataset from the given data 
node. After the program has finished running, the results can be stored on a 
data node again.

.. _section-tasks:

=================
Task Descriptions
=================

In this section we discuss the steps required to perform several tasks. 

Upload Dataset
==============

1. Request from a random central manager a data node that is available and has 
   enough diskspace for the new dataset
2. The client uploads the data to the given data node, using rsync. Rsync makes
   sure the data uploaded is actually correct.
3. The client notifies a central manager when the upload has finished
4. The central manager coordinates the data duplication, and makes sure the 
   dataset is stored on two data nodes.

A schematic overview can be seen in :numref:`fig-upload`. All this 
communication is transient: it only makes sense to transfer the data if the 
data node is available.

.. _fig-upload:

.. figure:: img/upload.png
    :scale: 50 %

    Schematic overview of all steps required to upload a dataset.


Job Request
===========

1. Client sends a job request to the manager: which kind of program, on which 
   dataset
2. Central manager divides the job in subtasks, by asking the corresponding
   data node to parse the dataset, and return byte offsets where a dataset can
   be split (not shown in the image). Each subtask is put on the queue, and 
   available workers can pick these subtasks from this queue.
3. Worker nodes download the corresponding datasets or chunks from the data 
   nodes, and start performing the task.
4. Results can be stored on data nodes again.

A schematic overview can be found in :numref:`fig-job-request`. Most of this 
communication is persistent: clients can send a persistent message to the 
central manager, and can periodically check if their job has finished 
afterwards. 

.. _fig-job-request:

.. figure:: img/job_request.png
    :scale: 50 %

    Steps to perform a large job

Performing a subtask
====================

1. *[persistent]* An available worker picks a job from the subtask queue. This task contains
   the following metadata: a dataset/file ID, which program, and the chunk
   start and end byte offsets.
2. *[transient]* A worker asks the central manager which data node to contact to retrieve the
   dataset. If the data node appears offline, the worker notifies the central
   manager, and the manager will send an alternate data node. 
3. *[transient]* The worker downloads the data chunk from the given data node.
4. The worker starts the program, and when finished stores the results back on
   the data node.

Currently, the program is always MAFFT [mafft]_, which can quickly calculate a 
multiple sequence alignment for large collections of genomes. It also supports 
merging
independent alignments to a single alignment, which is useful to merge all
results calculated by workers to a single alignment result.

If something goes wrong, and the worker can gracefully handle this error, we
notify the RabbitMQ server to requeue the subtask. The RabbitMQ server also 
checks if each worker is still alive, and when one worker dies without 
acknowledging the completion of a subtask, this subtask is again requeued.

When MAFFT finishes successfully the worker uploads the results to a data
node, and acknowledges the completion of a subtask to the RabbitMQ server.

.. [pgpool]
    pgPool-II, a PostgreSQL middleware. Available: http://pgpool.net

.. [rabbitmq]
    RabbitMQ: robust messaging for applications. Available: 
    https://rabbitmq.com

.. [mafft]
    Katoh, Kazutaka, and Daron M. Standley. "MAFFT multiple sequence alignment 
    software version 7: improvements in performance and usability." *Molecular 
    biology and evolution* 30.4 (2013): 772-780.
