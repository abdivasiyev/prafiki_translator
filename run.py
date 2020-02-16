import os
from application import server
from application.globals import HOST, PORT

if __name__ == '__main__':
    server.run(host=HOST, port=int(os.environ.get('PORT', PORT)))