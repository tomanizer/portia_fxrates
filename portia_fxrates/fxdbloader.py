## FX Rates from openexchangerates.org

import pandas as pd

from datetime import datetime
from dbtools.databases import *

from configurator import Configurator
from getpass import getuser
from porta_fxrates import getFX

import logging
logger = logging.getLogger(__name__)


def createDB(dbname):
    """Connect to a database. Database must be defined in the dbtools.databases module
    For this bcp module database must be of type MS SQL Server."""
    try:
        logger.debug("Getting DB connection...")
        db = eval(dbname+"()") # creating DB class
        db.engine.connect()
        logger.debug("Getting DB connection...succeeded")
        return db
    except Exception as e:
        logger.error("Database is not available. {}".format(e))
        raise

    
def convertFXDF(df, currlist=None):
    df = df[["base", "rates", "timestamp"]]
    #turn timestamp into local timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    df['timestamp'] = df['timestamp'].apply(lambda x:  x.tz_localize('UTC'), convert_dtype=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('Europe/London')
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)
    #df['timestamp']  = df['timestamp'].apply(lambda x: x.tz_convert('Europe/London'))
    if currlist is not None:
        df = df.loc[currlist]
    df = df.reset_index()
    df = df.rename(columns={'index': 'CURR'})
    df = df.set_index('CURR')
    df['UPDATED_ON'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['UPDATED_BY'] = getuser()
    #df['REMID'] = None
    #turn columns into upper
    for column in df.columns:
        df= df.rename(columns={column: column.upper()})
    logger.info("FX Rates: ".format(df.to_string(index=False)))
    return df
    
def FXtoDB():
 
    mydb = createDB(appconfig.dbname)

    try:
        fxdf = getFX()
    except Exception as e:
        logger.error("Could not retrieve FX. Error: {}".format(e))
        raise

    try:
        logger.info("Converting fx df into usable format")
        #fxdf = convertFXDF(fxdf, appconfig.currlist)
        fxdf = convertFXDF(fxdf)
        fxdf = fxdf.reset_index()
    except Exception as e:
        logger.error("Could not convert FX into table. {}".format(e))
        raise
       
    try:
        tablename = "MARKETDATA_OPENFX"
        logger.info("Loading FX into database {} into table {}.".format(appconfig.dbname, tablename))
        
        #delete data in table
        try:
            logger.debug("Deleting existing data from {}".format(tablename))
            sql = "DELETE from {}".format(tablename)
            connection = mydb.engine.connect()
            connection.execute(sql)
        except Exception as e:
            logger.warning("Could not delete table {}. Error: {}".format(tablename, e))
        
        fxdf.to_sql(tablename, con=mydb.engine, index=False, if_exists='append', schema='dbo')
        logger.info("Loading FX into database {}...Done.".format(appconfig.dbname))
    except Exception as e:
        logger.error("Could not upload FX to database {}. Error: {}".format(appconfig.dbname,e))
        raise
    return 0
 
if __name__ == '__main__':

    configurator = Configurator()
    configurator.parser.add_argument("-db", "--dbname", required=True, help="databasename for upload (must be available in dbtools)")
    
    global appconfig
    appconfig = configurator.configureApp(setuplogger=True)
    logger.info("Start")
    FXtoDB()
    logger.info("End")


