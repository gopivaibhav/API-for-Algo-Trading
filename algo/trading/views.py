# from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
# from rest_framework.parsers import JSONParser
# from .models import Article
# from .serializers import ArticleSerializer
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(req):
    return HttpResponse('Hello dude')

@csrf_exempt
def check(req,tit):
    returnVal=0
    symbol=tit
    from datetime import  date,timedelta
    from jugaad_data.nse import  stock_df

    # Download as pandas dataframe
    df = stock_df(symbol=symbol, from_date=date.today()-timedelta(days=200),
                to_date=date.today(), series="EQ")
    df.drop(['SERIES', 
           'VWAP', '52W H', '52W L', 'VOLUME', 'VALUE', 'NO OF TRADES', 'SYMBOL'],inplace=True,axis=1)
    df=df[::-1]
    df=df.reset_index()
    import numpy as np
    import pandas as pd

    pd.options.display.max_columns = None

    emadf = pd.DataFrame({'CLOSE':df['CLOSE']})

    emadf['EMA100'] = emadf['CLOSE'].ewm(span=100, min_periods=0, adjust=True).mean()
    emadf['EMA50'] = emadf['CLOSE'].ewm(span=50, min_periods=0, adjust=True).mean()

    ema100 = emadf['EMA100'].iloc[-1]
    ema50 = emadf['EMA50'].iloc[-1]

    rsidf = pd.DataFrame({'CLOSE':df['CLOSE']})

    def rma(x, n, y0):
        a = (n-1) / n
        ak = a**np.arange(len(x)-1, -1, -1)
        return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]

    n=14

    rsidf['change'] = rsidf['CLOSE'].diff()
    rsidf['change'][0] = 0
    rsidf['gain'] = rsidf.change.mask(rsidf.change < 0, 0.0)
    rsidf['loss'] = -rsidf.change.mask(rsidf.change > 0, -0.0)
    rsidf['avg_gain'] = rma(rsidf.gain[n+1:].to_numpy(), n, np.nansum(rsidf.gain.to_numpy()[:n+1])/n)
    rsidf['avg_loss'] = rma(rsidf.loss[n+1:].to_numpy(), n, np.nansum(rsidf.loss.to_numpy()[:n+1])/n)
    rsidf['rs'] = rsidf.avg_gain / rsidf.avg_loss
    rsidf['rsi_14'] = 100 - (100 / (1 + rsidf.rs))

    rsi = rsidf['rsi_14'][99]

    sodf = pd.DataFrame(df[-14::]) # get latest 14 days

    c = sodf['CLOSE'].iloc[-1]
    l = sodf['LOW'].min()
    h = sodf['HIGH'].max()

    so = (c-l)/(h-l) * 100


    delta = df['CLOSE'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=True).mean()
    ema_down = down.ewm(com=13, adjust=True).mean()
    rs = ema_up/ema_down

    df['RSI'] = 100 - (100/(1 + rs))
    df.RSI
    if (ema50>ema100):
          returnVal+=1
    if (rsi<30):
      returnVal+=1
    if (so<20):
      returnVal+=1
    return JsonResponse({'value':returnVal})
