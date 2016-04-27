.. _section-system-design:

System Design
=============

The general idea is to have a multi cluster architecture with centralized 
scheduling. There are three kind of nodes:

* Central manager nodes
* Data nodes
* Computational worker nodes

An overview of the system can be seen in :ref:`fig-overview`.

.. _fig-overview:

.. figure:: img/overview.png

    Global system overview

Central Managers
----------------

The central managers are the most intelligent nodes of the system, and try to 
coordinate the whole NGS pipeline. Central managers keep track which datasets 
are stored on which data nodes, the handle the request to perform some analysis
on a dataset. 

Central managers store a lot of metadata, and the idea is to replicate this 
data on all central managers. This data is stored in a PostgreSQL database, and
using pgPool-II it is possible to setup the replication system. The persistent 
messaging middleware also runs on the central manager, and in our case we use 
RabbitMQ as our message queue. RabbitMQ has built in functionality to share 
message queues across multiple nodes. 

We assume all nodes will be located in the same data center (it is a 
distributed system for a single company or research group), and therefore the 
chance of a network partition is considered low.

Data Nodes
----------

All datasets are stored on dedicated "data nodes". To prevent any data loss, 
and to retain high availability of the data, the central manager makes sure 
that each dataset is stored on two different nodes. Clients upload their data 
directly to the data node, but ask a central manager first which data node is 
suitable (enough disk space, other criteria).

Besides being a simple distributed file system, it also provides some more 
intelligent functionality: it parses the file to determine proper byte offsets 
to split a file in multiple chunks, while maintaining the structure in the 
data. 

Computational Worker Nodes
--------------------------

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

Task Descriptions
=================

In this section we discuss the steps required to perform several tasks. 

Upload Dataset
--------------

1. Request from a random central manager a data node that is available and has 
   enough diskspace for the new dataset
2. The client uploads the data to the given data node
3. The client notifies a central manager when the upload has finished
4. The central manager coordinates the data duplication, and makes sure the 
   dataset is stored on two data nodes.

A schematic overview can be seen in :ref:`fig-upload`.

.. _fig-upload:

.. figure:: img/upload.png
    :scale: 80 %

    Steps to upload a dataset


Job Request
-----------


