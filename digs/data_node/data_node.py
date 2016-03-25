from digs import db
from digs.data_node import data_handler


class DataNode(object):
    """This class handles retrieving, cutting, parsing and storing both incomming
    and out coming data.
    """

    def create_database(self, db_string):
        self.db_con = db.initialize_easy_db(db_string)
