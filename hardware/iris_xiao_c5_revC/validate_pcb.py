"""Read-only RevC PCB/schematic parity audit using KiCad 9 pcbnew.

Run with: python3 validate_pcb.py
Optional --board/--netlist/--output paths select a saved snapshot.
This compares physical pad net assignments and symbol/footprint identity.
Run native KiCad DRC separately to check actual copper geometry/connectivity.
"""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import pcbnew

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--board', type=Path, default=ROOT/'IRIS_C5_RevC.kicad_pcb')
parser.add_argument('--netlist', type=Path, default=ROOT/'output/native_netlist.xml')
parser.add_argument('--output', type=Path, default=ROOT/'output/pcb/netlist_parity.json')
args = parser.parse_args()
errors = []

def fail(kind, **details):
    errors.append({'kind': kind, **details})

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

board_hash = sha(args.board)
netlist_hash = sha(args.netlist)
xml = ET.parse(args.netlist).getroot()
main_schematic = ROOT/'IRIS_C5_RevC.kicad_sch'
match = re.search(r'\(uuid\s+"?([0-9a-fA-F-]+)', main_schematic.read_text())
if not match:
    raise SystemExit('Cannot find root schematic UUID')
root_uuid = match.group(1)
components = {}
for comp in xml.findall('./components/comp'):
    ref = comp.get('ref')
    if ref in components:
        fail('duplicate_schematic_reference', reference=ref)
    sheet_uuids = comp.find('sheetpath').get('tstamps', '/').strip('/')
    symbol_uuids = comp.findtext('tstamps', '').split()
    if len(symbol_uuids) != 1:
        fail('unexpected_schematic_instance_count', reference=ref, uuids=symbol_uuids)
    full_path = '/' + '/'.join(part for part in [root_uuid, sheet_uuids, symbol_uuids[0] if symbol_uuids else ''] if part)
    components[ref] = {'value': comp.findtext('value', ''),
                       'footprint': comp.findtext('footprint', ''),
                       'path': full_path}
expected = {}
expected_groups = defaultdict(set)
for net in xml.findall('./nets/net'):
    name = net.get('name')
    for node in net.findall('node'):
        ident = (node.get('ref'), node.get('pin'))
        if ident in expected:
            fail('duplicate_schematic_pin', reference=ident[0], pin=ident[1])
        expected[ident] = name
        expected_groups[name].add(ident)
expected_nc = {ident for ident, name in expected.items() if name.startswith('unconnected-')}
for ident in expected_nc:
    if len(expected_groups[expected[ident]]) != 1:
        fail('nc_network_has_multiple_pins', reference=ident[0], pin=ident[1], net=expected[ident])
if len(expected) != 225 or len(expected_nc) != 37:
    fail('unexpected_revc_pin_counts', total=len(expected), nc=len(expected_nc))
if len(components) != 62:
    fail('unexpected_revc_component_count', count=len(components))

board = pcbnew.LoadBoard(str(args.board))
footprints = defaultdict(list)
ignored_mounting_holes = []
ignored_paste_pads = Counter()
mechanical_pads = []
actual = defaultdict(list)
component_checks = []
for footprint in board.GetFootprints():
    ref = footprint.GetReference()
    pads = list(footprint.Pads())
    if ref in {'H1', 'H2', 'H3', 'H4'}:
        if not pads or any(p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH or p.GetNetCode() != 0 or p.GetNetname() for p in pads):
            fail('mounting_hole_is_electrical', reference=ref)
        ignored_mounting_holes.append(ref)
        continue
    footprints[ref].append(footprint)
    if ref not in components:
        fail('extra_board_component', reference=ref)
    for pad in pads:
        number = pad.GetNumber()
        layers = set(pad.GetLayerSet().Seq())
        if not number:
            # Only genuine paste-only apertures may be absent from the schematic.
            if layers and layers <= {pcbnew.F_Paste, pcbnew.B_Paste} and not pad.GetNetname() and pad.GetNetCode() == 0:
                ignored_paste_pads[ref] += 1
                continue
            fail('unexpected_unnumbered_pad', reference=ref,
                 layers=[board.GetLayerName(layer) for layer in sorted(layers)], net=pad.GetNetname())
            continue
        if ref == 'J3' and number == 'MP':
            if pad.GetNetname() or pad.GetNetCode() != 0:
                fail('mechanical_mount_pad_has_network', reference=ref, pin=number, net=pad.GetNetname())
            mechanical_pads.append({'reference': ref, 'pin': number, 'net': pad.GetNetname()})
            continue
        if not any(pcbnew.IsCopperLayer(layer) for layer in layers):
            fail('numbered_pin_has_no_copper', reference=ref, pin=number)
        actual[(ref, number)].append(pad.GetNetname())

for ref, expected_meta in sorted(components.items()):
    items = footprints.get(ref, [])
    if len(items) != 1:
        fail('board_reference_count', reference=ref, expected=1, actual=len(items))
        continue
    fp = items[0]
    fpid = fp.GetFPID()
    meta = {'value': fp.GetValue(),
            'footprint': str(fpid.GetLibNickname()) + ':' + str(fpid.GetLibItemName()),
            'path': fp.GetPath().AsString()}
    issues = [field for field in expected_meta if expected_meta[field] != meta[field]]
    if issues:
        fail('component_identity_mismatch', reference=ref, fields=issues,
             expected=expected_meta, actual=meta)
    component_checks.append({'reference': ref, 'result': 'PASS' if not issues else 'FAIL',
                             'value': meta['value'], 'footprint': meta['footprint'], 'path': meta['path']})
for ref, items in footprints.items():
    if len(items) > 1 and ref not in components:
        fail('duplicate_extra_board_reference', reference=ref, count=len(items))
for ident in actual.keys() - expected.keys():
    fail('extra_electrical_pad', reference=ident[0], pin=ident[1], networks=actual[ident])
pin_checks = []
for ident, name in sorted(expected.items()):
    nets = actual.get(ident, [])
    good = bool(nets) and all(net == name for net in nets)
    if not good:
        fail('pad_net_mismatch' if nets else 'missing_physical_pad', reference=ident[0],
             pin=ident[1], expected=name, actual=nets)
    pin_checks.append({'reference': ident[0], 'pin': ident[1],
                       'classification': 'NC' if ident in expected_nc else 'connected',
                       'expected_net': name, 'physical_pad_nets': nets,
                       'result': 'PASS' if good else 'FAIL'})
if sorted(ignored_mounting_holes) != ['H1', 'H2', 'H3', 'H4']:
    fail('mounting_hole_set_mismatch', actual=sorted(ignored_mounting_holes))
if len(mechanical_pads) != 2:
    fail('fpc_mechanical_pad_count', expected=2, actual=len(mechanical_pads))
if sha(args.board) != board_hash or sha(args.netlist) != netlist_hash:
    fail('input_changed_during_validation', hint='Rerun after the board/netlist write finishes')

report = {
    'result': 'PASS' if not errors else 'FAIL',
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'kicad_version': pcbnew.Version(),
    'board': str(args.board.resolve()), 'board_sha256': board_hash,
    'native_netlist': str(args.netlist.resolve()), 'native_netlist_sha256': netlist_hash,
    'schematic_components': len(components),
    'electrical_board_footprints': sum(len(fs) for fs in footprints.values()),
    'logical_physical_pin_ids': len(expected),
    'connected_pin_ids': len(expected)-len(expected_nc),
    'explicit_nc_pin_ids': len(expected_nc),
    'numbered_electrical_copper_pad_instances': sum(len(v) for v in actual.values()),
    'duplicate_pin_pad_instances': {f'{ref}.{pin}': len(nets) for (ref,pin),nets in actual.items() if len(nets)>1},
    'ignored_npth_mounting_holes': sorted(ignored_mounting_holes),
    'ignored_unnumbered_paste_apertures': dict(sorted(ignored_paste_pads.items())),
    'unconnected_fpc_mechanical_pads': mechanical_pads,
    'component_checks': component_checks,
    'pin_checks': pin_checks,
    'errors': errors,
    'method': 'Read native schematic XML and saved PCB with pcbnew. Compare every electrical physical pad net, including duplicated pad numbers and 37 NC pin IDs; compare value, footprint library ID, and full schematic instance path.',
    'scope': 'Pad net assignment and component identity parity only. Native PCB DRC must separately verify actual routed copper connectivity, clearance, and fabrication rules.',
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({key: value for key, value in report.items() if key not in {'component_checks','pin_checks'}}, ensure_ascii=False, indent=2))
if errors:
    sys.exit(1)
