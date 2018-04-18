import pyodbc
import pymssql
from logger_mod import Logger

class DAO(object):
   def __init__(self, connstring):
       self.connstring = connstring

   def execute_query(self, query):
       rows = []
       cnxn = None
       try:
           cnxn = pyodbc.connect(self.connstring, autocommit=True)
           cursor = cnxn.cursor()
           cursor.execute(query)
           rows = cursor.fetchall()
           Logger.logger.debug("Running query: {0}".format(query))
           Logger.logger.debug(rows)
       except Exception as e:
           Logger.logger.error(e)
       finally:
           if cnxn:
               cnxn.close()
       return rows

   #  This command is used for Insert, Update and Delete operations which returns row count
   def execute_non_query(self, query):
       rows = 0
       cnxn = None
       try:
           if query:
               cnxn = pyodbc.connect(self.connstring, autocommit=True)
               cursor = cnxn.cursor()
               cursor.execute(query)
               rows = cursor.rowcount
               Logger.logger.debug("Running query: {0}".format(query))
               Logger.logger.debug(rows)
           else:
              Logger.logger.error("Please input query")
       except Exception as e:
           Logger.logger.error(e)
       finally:
           if cnxn:
               cnxn.close()

       return rows

   def execute_callproc_query(self, query):
       db_attr = dict()
       result = []
       cnxn = None
       temp = self.connstring.split(";")
       for t in temp:
           attr = t.split("=")
           db_attr[attr[0]] = attr[1]

       try:
           if db_attr['sp']:
               with pymssql.connect(db_attr['SERVER'], db_attr['UID'], db_attr['PWD'], db_attr['DATABASE']) as conn:
                  with conn.cursor(as_dict=True) as cursor:
                      cursor.execute("use {0}".format(db_attr['DATABASE']))
                      cursor.callproc(query)
                      for row in cursor:
                          result.append(row)
                      Logger.logger.debug("Running sp call: {0}".format(query))
                      Logger.logger.debug(result)
           else:
              Logger.logger.error("Please input stored procedure.")
       except Exception as e:
           Logger.logger.error(e)
       finally:
           if cnxn:
              cnxn.close()

       return result