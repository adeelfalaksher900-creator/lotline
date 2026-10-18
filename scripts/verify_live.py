"""Exercise only the new synthetic Lotline deployment. No real data involved."""
import json,urllib.request,urllib.error,http.cookiejar
from pathlib import Path
base='https://lotline-eight-indol.vercel.app'
jar=http.cookiejar.CookieJar();client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def call(path,body=None,csrf=None):
 headers={'User-Agent':'Lotline-Verification/1.0'}
 if body is not None:headers.update({'Content-Type':'application/json','x-lotline-csrf':csrf or ''})
 r=client.open(urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers),timeout=55)
 return json.load(r)
workspace=call('/api/workspace')
csrf=workspace['csrf']
one=call('/api/investigate',{'question':'one hop','lot_id':'LOT-SM-2407','depth':1,'use_agent':False},csrf)
assert one['totals']['units']==0
full=call('/api/investigate',{'question':'Compare one hop with the full chain for LOT-SM-2407','lot_id':'LOT-SM-2407','depth':6,'use_agent':True},csrf)
assert full['totals']['units']==1180,full
assert full['totals']['review_units']==300
unknown=call('/api/investigate',{'question':'trace LOT-NOT-REAL','lot_id':'LOT-NOT-REAL','depth':6,'use_agent':False},csrf)
assert unknown['outcome']=='unknown_lot'
plan=call('/api/plan',{'lot_id':'LOT-SM-2407'},csrf)
committed=call('/api/commit',{'token':plan['token'],'approved':True},csrf)
replayed=call('/api/commit',{'token':plan['token'],'approved':True},csrf)
assert committed['decision']['units']==1180
assert replayed['replayed'] is True
summary={'health':'passed','one_hop_units':one['totals']['units'],'full_units':full['totals']['units'],'review_units':full['totals']['review_units'],'planner':full['planner']['mode'],'model':full['planner']['model'],'unknown':'passed','reviewed_action':'passed','replay':'passed','records':len(workspace['graph']['nodes'])}
Path('docs/live-verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
