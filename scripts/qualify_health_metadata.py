"""Prove one reviewed metadata-only transition without weakening byte contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from export_release_contract import snapshot
from verify_release_candidate import verify

ROOT = Path(__file__).resolve().parents[1]


def prove(before, after, definition, installer):
    if before.keys() != after.keys() or any(before[k] != after[k] for k in before if k != 'packaged_file_sha256'):
        raise ValueError('Contract shape or coverage changed')
    old, new = before['packaged_file_sha256'], after['packaged_file_sha256']
    if old.keys() != new.keys():
        raise ValueError('Runtime inventory changed')
    changed = {name for name in old if old[name] != new[name]}
    path = definition['runtime_path']
    if changed != {path} or old[path] != definition['before_sha256'] or new[path] != definition['after_sha256']:
        raise ValueError('Not the exact reviewed health metadata transition')
    if installer != definition['dist_info_sha256']:
        raise ValueError('Installer metadata or resources changed')


def qualify(wheel, output):
    definition = json.loads((ROOT / 'compatibility/health-field-metadata.json').read_text())
    baseline_manifest = json.loads((ROOT / 'releases/candidate/release.json').read_text())
    baseline = (ROOT / 'releases/candidate/contract.json').read_bytes()
    recorded = baseline_manifest['components']['controlplane-api']
    if (baseline_manifest.get('schema_version') != 1
            or set(baseline_manifest.get('components', {})) != {'controlplane-api'}
            or baseline_manifest.get('line') != definition['version'].rsplit('.', 1)[0]
            or recorded['artifact']['kind'] != 'package'
            or recorded['artifact']['uri'] != 'urn:sha256:' + definition['baseline_wheel_sha256']
            or hashlib.sha256(baseline).hexdigest() != definition['baseline_contract_sha256']
            or recorded['contract_sha256'] != definition['baseline_contract_sha256']
            or recorded['artifact']['sha256'] != definition['baseline_wheel_sha256']
            or recorded['version'] != definition['version']):
        raise ValueError('Historical qualification differs from verified baseline')
    contract, evidence = snapshot(wheel)
    if evidence['version'] != definition['version']:
        raise ValueError('This transition does not authorize a version change')
    with zipfile.ZipFile(wheel) as archive:
        prefix = f"controlplane_api-{definition['version']}.dist-info/"
        installer = {name.removeprefix(prefix): hashlib.sha256(archive.read(name)).hexdigest()
                     for name in archive.namelist() if name.startswith(prefix) and name != prefix + 'RECORD'}
    before = json.loads(baseline)
    after = json.loads(contract)
    policy_path = ROOT / 'compatibility/password-policy.json'
    policy = json.loads(policy_path.read_text())
    runtime_path = 'controlplane_api/utils.py'
    if (before['packaged_file_sha256'][runtime_path] != policy['before_sha256']
            or after['packaged_file_sha256'][runtime_path] != policy['after_sha256']
            or evidence['wheel_sha256'] != policy['wheel_sha256']):
        raise ValueError('Password policy transition differs from the declared candidate')
    # Validate the historical health transition independently of the new policy.
    health_only = json.loads(contract)
    health_only['packaged_file_sha256'][runtime_path] = policy['before_sha256']
    prove(before, health_only, definition, installer)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'contract.json').write_bytes(contract)
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    manifest = {'schema_version': 1, 'line': definition['version'].rsplit('.', 1)[0], 'components': {
        'controlplane-api': {'version': definition['version'], 'contract': 'contract.json',
                            'contract_sha256': evidence['contract_sha256'],
                            'artifact': {'kind': 'package', 'sha256': evidence['wheel_sha256'],
                                         'uri': 'urn:sha256:' + evidence['wheel_sha256']}}}}
    (output / 'release.json').write_text(json.dumps(manifest, indent=2) + '\n')
    verify(output / 'release.json', output / 'contract.json', output / 'evidence.json', 'controlplane-api')
    receipt = {'schema_version': 1, 'kind': 'development-password-policy-change',
               'password_policy_definition_sha256': hashlib.sha256(policy_path.read_bytes()).hexdigest(), 'stable_release': False,
               'baseline_wheel_sha256': definition['baseline_wheel_sha256'],
               'baseline_contract_sha256': definition['baseline_contract_sha256'],
               'candidate_wheel_sha256': evidence['wheel_sha256'],
               'candidate_contract_sha256': evidence['contract_sha256'],
               'definition_sha256': hashlib.sha256((ROOT / 'compatibility/health-field-metadata.json').read_bytes()).hexdigest()}
    (output / 'compatibility.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wheel', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    qualify(args.wheel, args.output)
    print('Health metadata and password policy transitions verified; source qualification only')
