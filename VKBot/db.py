from Database.Connector import DbSession
from Database.Models import CommandModel

db = DbSession(CommandModel.CommandModel)
db.create_table()