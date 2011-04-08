import urllib, urllib2, re, csv
from datetime import datetime, timedelta

class FinamData:

    def __init__(self):
        f = urllib.urlopen("http://www.finam.ru/scripts/export.js")
        lines = f.readlines()    
                    
        def parsetuple(s, trans=str):
            s = s.strip(" \t()")
            return [trans(val) for val in s.split(",")]

        for line in lines:
            m = re.match(r"var\s+(\w+)\s*=\s*new\s+Array\s*(.*);", line)
            varname = m.group(1)
            varval = m.group(2)
            if varname == "aEmitentIds":
                aEmitentIds = parsetuple(varval, int)
            elif varname == "aEmitentCodes":
                aEmitentCodes = parsetuple(varval.replace("'", ""))
            elif varname == "aEmitentMarkets":
                aEmitentMarkets = parsetuple(varval, int)
                
        # Split codes and ids into pairs
        pairs = zip(aEmitentMarkets, aEmitentIds)
        self.DATABASE = dict(zip(aEmitentCodes, pairs))

        self.resolutions = {
            timedelta(minutes=1):  2,
            timedelta(minutes=5):  3,
            timedelta(minutes=10): 4,
            timedelta(minutes=15): 5,
            timedelta(minutes=30): 6,
            timedelta(hours=1):    7,
            timedelta(days=1):     8,
            timedelta(weeks=1):    9,
        }

    def read(self, ticker, start, end, period):
        """
        Finds ticker in the finam's database stored in export.js file which parsed before
        and trying to find data in a cache or if not download data from a remote service
        and save into cache for further using.
        """
        fmt = "%y%m%d" # Date format of request
        dfrom = start.date()
        dto = end.date()
        fname = "{0}_{1}_{2}".format(ticker, dfrom.strftime(fmt), dto.strftime(fmt))
        fext = ".csv"
        # Resolution
        try:
            p = self.resolutions[period]
        except KeyError:
            raise ValueError("Illegal value of period.")
        # Load file from finam if haven't ever loaded
        rdict = dict(d='d',
                     market=self.DATABASE[ticker][0],
                     cn=ticker,
                     em=self.DATABASE[ticker][1],
                     p=p,
                     yf=dfrom.year,
                     mf=dfrom.month-1, # In service month's numbers starts from 0
                     df=dfrom.day,
                     yt=dto.year,
                     mt=dto.month-1,
                     dt=dto.day,
                     dtf=1,  # Equals %Y%m%d
                     tmf=1,  # Equals %M%H%S
                     MSOR=0, # Begin of candles
                     sep=3,  # Semicolon ';'
                     sep2=1, # Not set a digit position delimiter
                     datf=5, # Format: DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL
                     f=fname,
                     e=fext,
                     at=0, # No header
                     )
        
        url = ("http://195.128.78.52/{f}{e}?" + 
              "d=d&market={market}&em={em}&df={df}&" + 
              "mf={mf}&yf={yf}&dt={dt}&mt={mt}&yt={yt}&" + 
              "p={p}&f={f}&e={e}&cn={cn}&dtf={dtf}&tmf={tmf}&" +
              "MSOR={MSOR}&sep={sep}&sep2={sep2}&datf={datf}&at={at}").format(**rdict)
        req = urllib2.Request(url)
        req.add_header('Referer', "http://www.finam.ru/analysis/export/default.asp")
        return urllib2.urlopen(req)
