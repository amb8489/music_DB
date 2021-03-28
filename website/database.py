from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

class DB_interface:
    def __init__(self, db):
        engine = db.get_engine();
        Base = automap_base()
        Base.prepare(engine, reflect=True)
        self.db = db
        self.session = Session(engine)





#

# import os
# import sys
# import glob
# import string
# import time
# import datetime
# import numpy as np
# directory = 'website/songs/dataset'
#
# for filename in os.listdir(directory):
#     if filename.endswith(".txt"):
#         path =directory+"/"+filename
#         with open(path,"r") as f:
#             for line in f:
#                 print(f.readline())
#                 time.sleep(1)
