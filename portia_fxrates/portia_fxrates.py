
## FX Rates from openexchangerates.org

import logging
logger = logging.getLogger(__name__)

import pandas as pd
import argparse
import ast
from datetime import datetime

try:
    from config import app_id
except ImportError:
    logger.error("Please add openfx app_id to configfile")
    raise

#settings for pandas display
pd.set_option('display.max_rows', 500)

#open FX Rates
baseurl = "http://openexchangerates.org/api"

#Set the proxy
#os.environ["http_proxy"] = "http://t371548:!Tgtlse99@inet-proxy-b.appl.swissbank.com:8080"

def getFX(currlist=None, cobdate = None):
    if cobdate is None:
        endpoint = "/latest.json?app_id=" + app_id
        cobdate = datetime.strftime(datetime.today(), '%Y%m%d')
    else:
        cobdate = str(cobdate)
        cobdate = "-".join([cobdate[:3], cobdate[4:5], cobdate[6:7]])
        endpoint = "/historical/" + cobdate + ".json?app_id=" + app_id
    url = baseurl + endpoint   
    logger.info("getting FX rates from: {}".format(url))
    df = pd.read_json(url)
    df = df[["base", "rates", "timestamp"]]
    if currlist is not None:
        df = df.loc[currlist]
    df = df.reset_index()
    df = df.rename(columns={'index': 'CURR'})
    df = df.set_index('CURR')
    df['cobdate'] = cobdate
    logger.info("FX Rates: ".format(df.to_string(index=False)))
    return df



if __name__ == '__main__':  
    
    parser = argparse.ArgumentParser(description="FX Rates from OpenExchangerates.org")
    parser.add_argument("-curr", "--currlist", help="Currencylist in list format ['EUR', 'CHF'] ", type=ast.literal_eval)
    args = parser.parse_args()
    fx = getFX(args.currlist)
    fx.to_clipboard(index=False)
    print(fx.to_string(index=False))