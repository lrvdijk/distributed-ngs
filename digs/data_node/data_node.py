from digs.exc import InvalidChunkSizeError
from digs.data_node import data_handler
from digs import db
import logging



class DataNode(object):
    """This class handles retrieving, cutting, parsing and storing both incomming
    and out coming data.
    """

    def create_database(self, db_string):
        self.db_con = db.initialize_easy_db(db_string)

    def get_chunk(self, payload):
        para = payload.get('parameters')
        try:
            chunk = data_handler.get_data_chunk(para[0], int(para[1]), int(para[2]))
        except InvalidChunkSizeError:
            logging.warning("Chunk could not be received.")
            return None
        return chunk
