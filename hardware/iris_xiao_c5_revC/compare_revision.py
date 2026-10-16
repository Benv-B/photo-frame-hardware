"""Audit the intended RevB -> RevC electrical changes, beyond native ERC."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
old={c['ref']:c for c in json.loads((R/'validation/revB_baseline/connectivity.json').read_text()) if not c['ref'].startswith('#')}
new={c['ref']:c for c in json.loads((R/'output/connectivity.json').read_text()) if not c['ref'].startswith('#')}
expected_removed={'R3','R17','Q6','Q8'}
allowed_modified={'U1','U2','U3','U4','Q7','L1','R1'}
def simple(c):
 return {'value':c['value'],'footprint':c['footprint'],'pins':{p['num']:{k:p[k] for k in ['name','net','type']} for p in c['pins']}}
changed={ref:{'before':simple(old[ref]),'after':simple(new[ref])} for ref in old.keys() & new.keys() if simple(old[ref])!=simple(new[ref])}
errors=[]
if old.keys()-new.keys()!=expected_removed:errors.append('Unexpected removed references')
if new.keys()-old.keys():errors.append('Unexpected added references')
if set(changed)!=allowed_modified:errors.append('Modified references differ from authorized plan')
assert all(p['net'] not in ('BOOST_PG','PG_N','OE_MID') for c in new.values() for p in c['pins'])
expect={('U1','1'):'FB',('U1','2'):'EN_LATCH',('U1','3'):'VBAT',('U1','4'):'GND',('U1','5'):'SW',('U1','6'):'5V_BOOST',('U2','3'):'EN_LATCH',('U4','3'):None,('Q7','3'):'BUS_OE_N'}
for (ref,pin),net in expect.items():
 if next(p['net'] for p in new[ref]['pins'] if p['num']==pin)!=net:errors.append(f'Unexpected net on {ref}.{pin}')
report={'result':'PASS' if not errors else 'FAIL','physical_components_before':len(old),'physical_components_after':len(new),'removed_references':sorted(old.keys()-new.keys()),'added_references':sorted(new.keys()-old.keys()),'modified_references':sorted(changed),'unchanged_components':len(old.keys() & new.keys())-len(changed),'changes':changed,'errors':errors,'note':'RevC intentionally changes the circuit; this is an authorized revision audit, not an unchanged-network claim.'}
(R/'output/revision_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='changes'},ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
