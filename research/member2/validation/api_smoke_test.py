"""Optional smoke test, Python standard library only.
Usage: python api_smoke_test.py http://127.0.0.1:8000
For an events/process POST, provide a sample request JSON path as second argument after confirming API contract.
"""
import json,sys,urllib.request,urllib.error
base=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8000').rstrip('/')
def call(path, payload=None):
    headers={'Accept':'application/json'}
    if payload is not None: headers['Content-Type']='application/json'
    req=urllib.request.Request(base+path,data=json.dumps(payload).encode() if payload is not None else None,headers=headers,method='POST' if payload is not None else 'GET')
    try:
        with urllib.request.urlopen(req,timeout=12) as r:
            print(path, 'HTTP', r.status, r.read().decode('utf-8')[:8000])
    except (urllib.error.URLError,TimeoutError) as exc: print(path,'FAILED:',exc)
call('/health')
if len(sys.argv)>2:
    with open(sys.argv[2],encoding='utf-8') as f: call('/events/process',json.load(f))
