import sqlite3
from sqlite3 import Error

class Connection :
  """
  Parameters :
    name :str the name of the db connection
  """
  def __init__(self, name : str) :
    self.name = name
    self.connection = None

  def open(self) :
    try :
      self.connection = sqlite3.connect(self.name)
    except Error as e :
      print(f"error {e} with database {self.name}")

  def close(self) :
    self.connection.close()

  def __enter__(self) :
    self.open()
    return self
  
  def __exit__(self, exc_type, exc_value, exc_tb) :
    self.close()

  def add_item(self, name : str, file_path : str, category : str) :
    print("Adding to db")
    cursor = self.connection.cursor()
    query = """INSERT into Assets (name, file_path, category) VALUES(?,?,?)"""
    query_data = (name, file_path, category)
    cursor.execute(query, query_data)
    self.connection.commit()