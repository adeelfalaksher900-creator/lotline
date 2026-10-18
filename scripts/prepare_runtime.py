"""Bundle verified Ubuntu native runtime for FalkorDB on older serverless hosts.

This never replaces the host libc. Only the graph child process uses this loader.
Package hashes are published by packages.ubuntu.com. Source and copyright notices
ship alongside the generated runtime. No binary is checked into the source repo.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request
import zstandard

ROOT=Path(__file__).resolve().parent.parent
TARGET=ROOT/'vendor/glibc'
PACKAGES=[
 ('libc6','https://security.ubuntu.com/ubuntu/pool/main/g/glibc/libc6_2.39-0ubuntu8.9_amd64.deb','ff5557d99b51f761c4b7c92368b9cc45565eda17df9bf9eb4b134d09825008be',{'libc.so.6':'libc.so.6','libm.so.6':'libm.so.6','ld-linux-x86-64.so.2':'ld-linux-x86-64.so.2'}),
 ('libstdc++6','https://security.ubuntu.com/ubuntu/pool/main/g/gcc-14/libstdc++6_14.2.0-4ubuntu2~24.04.1_amd64.deb','a51f8de7829211db961a31f02158058ad1a95f92ac6d0a5dff6350e2821c54c0',{'libstdc++.so.6.0.33':'libstdc++.so.6'}),
 ('libgcc-s1','https://security.ubuntu.com/ubuntu/pool/main/g/gcc-14/libgcc-s1_14.2.0-4ubuntu2~24.04.1_amd64.deb','aa7fadbe33b78bcf99885318040601c550c208929565b179891d9a3cc2aa68cd',{'libgcc_s.so.1':'libgcc_s.so.1'}),
 ('libgomp1','https://security.ubuntu.com/ubuntu/pool/main/g/gcc-14/libgomp1_14.2.0-4ubuntu2~24.04.1_amd64.deb','e8a95ec58125b4933597f30ff56c2ae10edf90f287262e366d4b6edea3019144',{'libgomp.so.1.0.0':'libgomp.so.1'}),
]

def archive_payload(deb):
 if not deb.startswith(b'!<arch>\n'):raise ValueError('Invalid Debian archive')
 pos=8
 while pos+60<=len(deb):
  header=deb[pos:pos+60];name=header[:16].decode().strip().rstrip('/');size=int(header[48:58]);data=deb[pos+60:pos+60+size]
  if name.startswith('data.tar'):
   if name.endswith('.zst'):data=zstandard.ZstdDecompressor().decompress(data,max_output_size=50_000_000)
   return tarfile.open(fileobj=io.BytesIO(data),mode='r:*')
  pos+=60+size+(size%2)
 raise ValueError('Missing package payload')

def prepare(destination=None):
 global TARGET
 if destination is not None:
  TARGET=Path(destination)
 TARGET.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for name,url,digest,files in PACKAGES:
  cache=Path('/tmp')/('lotline-'+name.replace('+','p')+'.deb')
  raw=cache.read_bytes() if cache.exists() else urllib.request.urlopen(url,timeout=60).read()
  if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Native package integrity check failed: '+name)
  cache.write_bytes(raw)
  found=set()
  with archive_payload(raw) as archive:
   for member in archive:
    basename=Path(member.name).name
    if member.isfile() and basename in files:
     dest=TARGET/files[basename];dest.write_bytes(archive.extractfile(member).read());dest.chmod(0o755);found.add(basename)
    if member.isfile() and member.name.endswith('/copyright'):
     dest=TARGET/'licenses'/name/'copyright';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(archive.extractfile(member).read())
  if found != set(files):raise ValueError('Native package does not contain expected libraries: '+name)
  manifest.append({'package':name,'url':url,'sha256':digest})
 (TARGET/'provenance.json').write_text(json.dumps(manifest,indent=2))
 (TARGET/'SOURCE.txt').write_text('Unmodified Ubuntu shared libraries. Copyright and licence notices are in licenses/. Corresponding source packages and build patches: https://packages.ubuntu.com/source/noble/glibc and https://packages.ubuntu.com/source/noble/gcc-14. Dynamic linking only; no host libraries are replaced.\n')
 print('Prepared verified native runtime:',', '.join(p.name for p in TARGET.glob('*.so*')))

if __name__=='__main__':prepare()
