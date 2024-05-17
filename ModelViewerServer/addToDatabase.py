#!/usr/bin/env python

import argparse
import Connection

def add_asset(database : str, name : str, file_path : str, category : str) :
  print("Adding asset to db")
  with Connection.Connection(database) as connection :
    connection.add_item(name, file_path, category)

if __name__ == "__main__" :
  parser = argparse.ArgumentParser(description = "Add asset to database")
  parser.add_argument("--name", "-n", help = "Name of asset to add", required = True)
  parser.add_argument("--file", "-f", help = "File path of asset to add", required = True)
  parser.add_argument("--category", "-c", help = "Category of asset", required = True)
  parser.add_argument("--database", "-db", help = "Which db to add to", required = True)

  args = parser.parse_args()

  add_asset(args.database, args.name, args.file, args.category)