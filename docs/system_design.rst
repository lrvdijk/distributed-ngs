.. _section-system-design:

System Design
=============

The general idea is to have a multi cluster architecture with centralized 
scheduling. There are three kind of nodes:

* Central manager nodes
* Data nodes
* Computational worker nodes

When clients want to store or retrieve data or perform some computational large
job, it should first ask the central manager, and from there it receives 
further instructions.



