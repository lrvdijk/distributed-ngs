from digs.manager.models import Data, DataNode, DataLoc, DataType
from digs.manager import ManagerServerProtocol, db
import time
from datetime import datetime


def main():

    # TODO: database settings in configuration file?
    db.initialize_db("sqlite:///manager.db")
    session = db.Session()
    db.create_tables()
    #
    # fasta1 = Data(title='FirstFastaFile',
    #                     size=495840,
    #                     type=DataType.FASTA,
    #                     upload_date=datetime.fromtimestamp(time.time()))
    # fasta2 = Data(title='SecondFastaFile',
    #                     size=495840,
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
    combi1 = DataLoc(data_id=1,
                          data_node_id=2,
                          file_path='DataFiles/DataNodes/testFasta.data', )
    # combi2 = DataLoc(data_id=2,
    #                       data_node_id=2,
    #                       file_path='DataFiles/DataNodes/testFasta.data', )
    session.add_all([combi1])
    session.commit()


if __name__ == '__main__':
    main()