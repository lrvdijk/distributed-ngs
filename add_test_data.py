from digs.manager.models import Data, DataNode, DataLoc, DataType, UploadJob
from digs.manager import db
import time
import datetime
from datetime import datetime


def main():

    # TODO: database settings in configuration file?
    db.initialize_db("sqlite:///manager.db")
    session = db.Session()
    db.create_tables()

    # fasta1 = Data(title='FirstFastaFile',
    #                     size=495840,
    #                     hash=222,
    #                     type=DataType.FASTA,
    #                     upload_date=datetime.fromtimestamp(time.time()))
    # fasta2 = Data(title='SecondFastaFile',
    #                     size=495840,
    #                     hash=111,
    #                     type=DataType.FASTA,
    #                     upload_date=datetime.fromtimestamp(time.time()))
    # data1 = DataNode(title='node1',
    #                  ip='192.0.0.1',
    #                  socket=5000,
    #                  location='Adam',
    #                  free_space=1000,
    #                  disk_space=2000,)
    # data2 = DataNode(title='node2',
    #                  ip='192.0.0.2',
    #                  socket=5002,
    #                  location='Adam2',
    #                  free_space=1000,
    #                  disk_space=2000, )
    #
    # session.add_all([fasta1,fasta2, data1, data2])
    # session.commit()
    # combi1 = DataNode(title='DataNode1',
    #                     ip='127.0.0.1',
    #                   socket=5673,
    #                   location='Rdam',
    #                   free_space=5953039,
    #                   disk_space=15953039,
    #                   )
    # combi2 = DataNode(title='DataNode2',
    #                   ip='127.0.0.1',
    #                   socket=5674,
    #                   location='Rdam2',
    #                   free_space=19953039,
    #                   disk_space=15953039,
    #                   )
    #
    # combi3 = DataLoc(data_id=2,
    #                       data_node_id=2,
    #                       file_path='/home/dwarrel/Courses/Distributed/distributed-ngs/DataFiles/DataNodes/5674', )

    new_job = UploadJob(data_node_id=1,
                        size=50,
                        type=DataType.FASTA,
                        upload_date=datetime.now(),
                        hash=123,
                        )
    session.add(new_job)
    session.commit()


if __name__ == '__main__':
    main()

