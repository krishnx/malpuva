import MySQLdb
from logger_mod import Logger

class L_DAO(object):
   def __init__(self, host="localhost", user="root", passwd="Alpha@1234", dbname="the_databases"):
       self.host = host
       self.user = user
       self.passwd = passwd
       self.dbname = dbname

   def execute_query(self, query):
       rows = []
       cnxn = None
       try:
           cnxn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.dbname)
           cursor = cnxn.cursor()
           cursor.execute(query)
           cnxn.commit()
           rows = cursor.fetchall()
           Logger.logger.debug("Running query: {0}.".format(query))
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
               cnxn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.dbname)
               cursor = cnxn.cursor()
               cursor.execute(query)
               cnxn.commit()
               rows = cursor.rowcount
               Logger.logger.debug("Running query: {0}".format(query))
               Logger.logger.debug(rows)
           else:
               Logger.logger.debug("Please provide query.")
       except Exception as e:
           Logger.logger.error(e)
       finally:
           if cnxn:
               cnxn.close()

       return rows