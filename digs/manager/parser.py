from digs.messaging.protocol import DigsProtocolParser

parser = DigsProtocolParser()

# TODO: Add JSON schema
parser.define_action("store_data", None)
parser.define_action("get_data", None)


@parser.register_handler("store_data")
async def store_data(protocol, payload):
    """This function handles a request from a client to store a new dataset."""
    # TODO: Implement this
