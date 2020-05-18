from Database.Connector import DbSession
from Database.Models import OsuModel

db = DbSession(OsuModel.OsuModel)
db.create_table()
