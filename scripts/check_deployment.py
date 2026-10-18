"""Read-only health probe. Does not print cookies or credentials."""
import urllib.request,urllib.error
for path in ['/api/health']:
 try:
  r=urllib.request.urlopen('https://lotline-eight-indol.vercel.app'+path,timeout=30)
  print(path,r.status,r.read().decode()[:6500])
 except urllib.error.HTTPError as e:print(path,e.code,e.read().decode()[:1000])
 except Exception as e:print(path,type(e).__name__,str(e))
