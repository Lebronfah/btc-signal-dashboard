from flask import Flask, jsonify, send_from_directory
import requests, time, math, statistics, datetime
from collections import deque, defaultdict
app=Flask(__name__,static_folder='.')
S=requests.Session(); S.headers.update({'User-Agent':'BTC-Signal-Research/1.0'})
prices=deque(maxlen=3600); cache={}; history={}
def get(url,params=None,ttl=0):
 k=(url,str(params)); now=time.time()
 if k in cache and now-cache[k][0]<ttl:return cache[k][1]
 try:
  r=S.get(url,params=params,timeout=5);r.raise_for_status();data=r.json();cache[k]=(now,data);return data
 except Exception:return cache.get(k,(None,None))[1]
def number(v,default=None):
 try:return float(v)
 except:return default
@app.get('/')
def home():return send_from_directory('.','index.html')
@app.get('/api/state')
def state():
 now=time.time(); boundary=int(now//300)*300; slug=f'btc-updown-5m-{boundary}'; remaining=300-(now-boundary)
 ticker=get('https://api.coinbase.com/v2/prices/BTC-USD/spot',ttl=2)
 price=number(((ticker or {}).get('data') or {}).get('amount'))
 if price:prices.append((now,price))
 ev=get('https://gamma-api.polymarket.com/events',{'slug':slug},ttl=8)
 event=ev[0] if isinstance(ev,list) and ev else {}; m=(event.get('markets') or [{}])[0]
 tokens=m.get('clobTokenIds') or [];outcomes=m.get('outcomes') or []
 import json
 if isinstance(tokens,str):
  try:tokens=json.loads(tokens)
  except:tokens=[]
 if isinstance(outcomes,str):
  try:outcomes=json.loads(outcomes)
  except:outcomes=[]
 books=[]
 for token in tokens[:2]:
  book=get('https://clob.polymarket.com/book',{'token_id':token},ttl=4) or {}
  bids=[number(x.get('price')) for x in book.get('bids',[])];asks=[number(x.get('price')) for x in book.get('asks',[])]
  bids=[x for x in bids if x is not None];asks=[x for x in asks if x is not None]
  books.append({'bid':max(bids) if bids else None,'ask':min(asks) if asks else None})
 while len(books)<2:books.append({'bid':None,'ask':None})
 start=next((p for t,p in prices if t>=boundary),None)
 # A missing opening sample is not silently replaced by the current price.
 obs=[(t,p) for t,p in prices if now-t<=180]
 model=None
 if start and price and len(obs)>=12:
  # Use returns sampled at least 2 seconds apart; avoid artificial confidence from rapid repeated polls.
  sampled=[];last=-1e20
  for t,p in obs:
   if t-last>=2:sampled.append((t,p));last=t
  if len(sampled)>=10:
   rr=[math.log(sampled[i][1]/sampled[i-1][1]) for i in range(1,len(sampled))]
   gaps=[sampled[i][0]-sampled[i-1][0] for i in range(1,len(sampled))]
   if len(rr)>=9 and statistics.stdev(rr)>0:
    vol=statistics.stdev(rr)/math.sqrt(statistics.mean(gaps)); z=math.log(price/start)/(vol*math.sqrt(max(1,remaining)))
    raw=.5*(1+math.erf(z/math.sqrt(2)))
    model=.5+(raw-.5)*min(.75,len(rr)/80)
 # Trades can be wallet-address ranked, but they cannot reliably identify named social-media traders.
 trades=[];whales=[]
 if m.get('conditionId'):
  raw=get('https://data-api.polymarket.com/trades',{'market':m['conditionId'],'limit':200},ttl=12)
  if isinstance(raw,list):
   sums=defaultdict(lambda:{'volume':0,'up':0,'down':0,'count':0})
   for tr in raw:
    addr=tr.get('proxyWallet') or tr.get('maker') or tr.get('taker')
    size=number(tr.get('size'),0);px=number(tr.get('price'),0);value=size*px
    if not addr or value<=0:continue
    x=sums[addr];x['volume']+=value;x['count']+=1
    outcome=str(tr.get('outcome','')).lower()
    if outcome=='up':x['up']+=value
    if outcome=='down':x['down']+=value
   whales=[{'wallet':w,'volume':round(x['volume'],2),'up':round(x['up'],2),'down':round(x['down'],2),'count':x['count']} for w,x in sorted(sums.items(),key=lambda kv:kv[1]['volume'],reverse=True)[:8]]
 # Estimate using the ASK (buyable price), with conservative 3 percentage-point cost buffer.
 signal='NO TRADE';why='Not enough reliable information to justify a trade.'
 if model is not None and len(books)==2 and all(b['ask'] is not None for b in books):
  upidx=next((i for i,o in enumerate(outcomes[:2]) if str(o).lower()=='up'),0);dnidx=1-upidx
  edgeup=model-books[upidx]['ask']-.03;edgedown=1-model-books[dnidx]['ask']-.03
  if edgeup>.06 and model>.60:signal='UP';why='Model estimate exceeds the executable UP ask by over 9 points including a cost buffer.'
  if edgedown>.06 and 1-model>.60 and edgedown>edgeup:signal='DOWN';why='Model estimate exceeds the executable DOWN ask by over 9 points including a cost buffer.'
  if signal=='NO TRADE':why='No sufficient edge versus the buyable Polymarket prices.'
 et=datetime.datetime.fromtimestamp(now,datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-5)))
 # Use zoneinfo for daylight saving.
 from zoneinfo import ZoneInfo
 et=datetime.datetime.fromtimestamp(now,ZoneInfo('America/New_York'))
 if et.hour<9:signal='WAIT';why='Signals begin at 9:00 AM Eastern.'
 if not event:signal='NO DATA';why='Current Polymarket round could not be verified.'
 return jsonify({'time':now,'price':price,'round':slug,'seconds_left':round(remaining),'start_proxy':start,'up_probability':model,'signal':signal,'reason':why,'market':event.get('title') or m.get('question') or slug,'market_url':'https://polymarket.com/event/'+slug,'outcomes':outcomes,'books':books,'whales':whales,'whale_source':'recent publicly reported trades in this round, not all BTC whales','social_status':'Not connected: X/YouTube/TikTok live posts require authorized feeds; no sentiment is invented.','samples':len(obs),'note':'Coinbase spot is NOT the Chainlink settlement TWAP. Model is experimental and unvalidated.'})
if __name__=='__main__':app.run(host='0.0.0.0',port=8080)
