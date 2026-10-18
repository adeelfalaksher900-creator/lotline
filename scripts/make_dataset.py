"""Reproducible fictional case. Contains no real company or customer data."""
import json
from pathlib import Path

nodes=[]; edges=[]
def node(id,kind,name,**props):
 nodes.append(dict(id=id,kind=kind,name=name,**props))
def edge(source,target,kind='INPUT_TO',evidence='confirmed',doc='',**props):
 edges.append(dict(source=source,target=target,kind=kind,evidence=evidence,source_id=doc,**props))
def document(id,title,body,at='2026-10-18T08:00:00Z'):
 node(id,'Document',title,body=body,at=at,synthetic=True)

document('DOC-01','Supplier alert · sesame lot SM-2407','FICTIONAL TRAINING RECORD. Supplier North Mill flags sesame lot LOT-SM-2407 after a packaging-label mismatch. This alert identifies the source lot only. It does not determine affected finished stock or declare any other lot safe.')
document('DOC-02','Mixing record · MIX-091','FICTIONAL TRAINING RECORD. Event EVT-01 consumed LOT-SM-2407 into MIX-091. Event EVT-02 consumed MIX-091 into LOT-CR-118. Both records are signed by the synthetic quality team.')
document('DOC-03','Repack record · LOT-RP-118','FICTIONAL TRAINING RECORD. EVT-03 repacked LOT-CR-118 into LOT-RP-118. A change of pack size retained the original batch lineage. Both retail and mini packs share the same upstream sesame lot.')
document('DOC-04','Rework record · LOT-RW-121','FICTIONAL TRAINING RECORD. EVT-04 used LOT-CR-118 as rework in LOT-RW-121. A new batch identifier does not erase the input relationship. Additional MIX-094 also fed LOT-RW-121.')
document('DOC-05','Mixing record · MIX-092','FICTIONAL TRAINING RECORD. EVT-05 consumed LOT-SM-2407 into MIX-092. EVT-06 produced LOT-SN-120 from MIX-092.')
document('DOC-06','Dispatch ledger · sesame products','FICTIONAL TRAINING RECORD. SH-101: 240 units of LOT-CR-118 to Alder Market. SH-102: 180 units to Harbor Grocer. SH-103: 360 mini packs LOT-RP-118 to Pine Stores. SH-104: 120 mini packs to Alder Market. SH-105: 200 LOT-SN-120 units at East Distribution. SH-106: 80 LOT-RW-121 units to Harbor Grocer.')
document('DOC-07','Unverified shift note · LOT-CR-119','FICTIONAL TRAINING RECORD. An unsigned shift note suggests LOT-CR-119 might contain LOT-SM-2407. The transformation manifest is missing. This relationship is UNVERIFIED and must not be promoted to confirmed exposure. SH-107 contains 300 units at Pine Stores. Obtain the missing signed batch record.')
document('DOC-08','Separate source record · LOT-SM-2408','FICTIONAL TRAINING RECORD. LOT-SM-2408 fed MIX-093, which produced LOT-CR-122. SH-108 contains 450 units at West Distribution. No path from LOT-SM-2407 to this stock is present in the supplied graph. Absence of that path is not a safety certificate.')
document('DOC-09','Supplier alert · milk powder MK-311','FICTIONAL TRAINING RECORD. Crescent Ingredients flags LOT-MK-311 for a label check. The lot fed MIX-095, then LOT-PR-211. SH-109 contains 150 units at Alder Market and SH-110 contains 90 units at Harbor Grocer.')
document('DOC-10','Packaging alert · PK-022','FICTIONAL TRAINING RECORD. Fold Paper flags LOT-PK-022 after an ink transfer report. It was used for LOT-PK-330. SH-111 contains 600 units at East Distribution. This scenario checks a packaging lineage rather than ingredient mixing.')

for id,name,location in [('SITE-A','Alder Market','North district'),('SITE-B','Harbor Grocer','Harbor district'),('SITE-C','Pine Stores','Central district'),('SITE-D','East Distribution','East district'),('SITE-E','West Distribution','West district')]:
 node(id,'Site',name,location=location)
for id,name in [('SUP-A','North Mill'),('SUP-B','Crescent Ingredients'),('SUP-C','Fold Paper')]:node(id,'Supplier',name)
lots=[
 ('LOT-SM-2407','Ingredient','Sesame · SM-2407',0,'sesame','Flagged supplier lot'),
 ('MIX-091','Mix','Sesame blend · 091',1,'sesame','Signed mixing record'),
 ('LOT-CR-118','Batch','Sesame crackers · 118',2,'crackers','Retail pack'),
 ('LOT-RP-118','Repack','Mini crackers · 118',3,'crackers','Repacked from batch 118'),
 ('LOT-RW-121','Rework','Seed bites · 121',3,'crackers','Includes reworked crackers'),
 ('MIX-092','Mix','Seed blend · 092',1,'sesame','Second mixing route'),
 ('LOT-SN-120','Batch','Sesame snack · 120',2,'snacks','Warehouse stock'),
 ('LOT-CR-119','Batch','Sesame crackers · 119',1,'crackers','Missing signed manifest'),
 ('LOT-SM-2408','Ingredient','Sesame · SM-2408',0,'sesame','Separate supplier lot'),
 ('MIX-093','Mix','Sesame blend · 093',1,'sesame','Separate production run'),
 ('LOT-CR-122','Batch','Sesame crackers · 122',2,'crackers','No link to flagged lot in graph'),
 ('MIX-094','Mix','Oat blend · 094',1,'oats','Second input to rework batch'),
 ('LOT-MK-311','Ingredient','Milk powder · MK-311',0,'milk','Label check'),
 ('MIX-095','Mix','Protein blend · 095',1,'milk','Signed mixing record'),
 ('LOT-PR-211','Batch','Protein bites · 211',2,'protein','Retail pack'),
 ('LOT-PK-022','Packaging','Carton stock · PK-022',0,'paper','Flagged packaging lot'),
 ('LOT-PK-330','Batch','Cartoned snack · 330',1,'snacks','Packaging route'),
]
for id,kind,name,stage,family,note in lots:node(id,kind,name,stage=stage,family=family,note=note)
for src,tar,doc in [('SUP-A','LOT-SM-2407','DOC-01'),('SUP-A','LOT-SM-2408','DOC-08'),('SUP-B','LOT-MK-311','DOC-09'),('SUP-C','LOT-PK-022','DOC-10')]:edge(src,tar,'SUPPLIED',doc=doc)
transforms=[('LOT-SM-2407','MIX-091','DOC-02'),('MIX-091','LOT-CR-118','DOC-02'),('LOT-CR-118','LOT-RP-118','DOC-03'),('LOT-CR-118','LOT-RW-121','DOC-04'),('MIX-094','LOT-RW-121','DOC-04'),('LOT-SM-2407','MIX-092','DOC-05'),('MIX-092','LOT-SN-120','DOC-05'),('LOT-SM-2408','MIX-093','DOC-08'),('MIX-093','LOT-CR-122','DOC-08'),('LOT-MK-311','MIX-095','DOC-09'),('MIX-095','LOT-PR-211','DOC-09'),('LOT-PK-022','LOT-PK-330','DOC-10')]
for i,(src,tar,doc) in enumerate(transforms):edge(src,tar,doc=doc,event_id=f'EVT-{i+1:02}',at='2026-10-17T09:00:00Z')
edge('LOT-SM-2407','LOT-CR-119',doc='DOC-07',evidence='unverified',event_id='EVT-U1',at='2026-10-17T10:00:00Z')
shipments=[('SH-101','LOT-CR-118','SITE-A',240,'delivered','DOC-06'),('SH-102','LOT-CR-118','SITE-B',180,'delivered','DOC-06'),('SH-103','LOT-RP-118','SITE-C',360,'delivered','DOC-06'),('SH-104','LOT-RP-118','SITE-A',120,'delivered','DOC-06'),('SH-105','LOT-SN-120','SITE-D',200,'warehouse','DOC-06'),('SH-106','LOT-RW-121','SITE-B',80,'delivered','DOC-06'),('SH-107','LOT-CR-119','SITE-C',300,'delivered','DOC-07'),('SH-108','LOT-CR-122','SITE-E',450,'warehouse','DOC-08'),('SH-109','LOT-PR-211','SITE-A',150,'delivered','DOC-09'),('SH-110','LOT-PR-211','SITE-B',90,'delivered','DOC-09'),('SH-111','LOT-PK-330','SITE-D',600,'warehouse','DOC-10')]
for id,lot,site,units,status,doc in shipments:
 node(id,'Shipment',id,units=units,status=status,stage=4,at='2026-10-17T14:00:00Z')
 edge(lot,id,'DISPATCHED',doc=doc)
 edge(id,site,'DELIVERED_TO',doc=doc)
for doc,target in [('DOC-01','LOT-SM-2407'),('DOC-07','LOT-CR-119'),('DOC-09','LOT-MK-311'),('DOC-10','LOT-PK-022')]:edge(doc,target,'ABOUT',doc=doc)

scenarios=[dict(id='sesame',lot_id='LOT-SM-2407',title='Sesame label mismatch',product='Sesame crackers & seed bites',severity='Priority',source_id='DOC-01',note='Mixing, repacking and a hidden rework route.',question='Trace LOT-SM-2407 through every transformation. Which shipments need a hold, and where is the evidence incomplete?'),dict(id='milk',lot_id='LOT-MK-311',title='Milk powder label check',product='Protein bites',severity='Review',source_id='DOC-09',note='One source, two retail destinations.',question='Investigate LOT-MK-311 and prepare a containment plan.'),dict(id='packaging',lot_id='LOT-PK-022',title='Carton ink transfer',product='Cartoned snacks',severity='Review',source_id='DOC-10',note='Trace the packaging, not the ingredient.',question='Which shipments used packaging LOT-PK-022?')]
payload=dict(version='2026-10-18.1',synthetic=True,nodes=nodes,edges=edges,scenarios=scenarios)
Path('data/scenario.json').write_text(json.dumps(payload,indent=2))
print(f'{len(nodes)} nodes, {len(edges)} edges, {len(scenarios)} cases')
