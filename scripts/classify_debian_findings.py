"""Classify exact reviewed Debian archive bytes and nested finding coordinates."""
import hashlib
from pathlib import Path


def classify(findings, layers, manifest, baseline):
    archives = {a['filename']: a for s in manifest['sources'] for a in [s['descriptor'], *s['archives']]}
    known = {(r['archive'], r['member']): r for r in baseline['members']}
    verified = {}
    accepted = 0
    unexpected = []
    for finding in findings:
        filename, separator, member = finding['File'].partition('!')
        path = Path(filename).resolve()
        try:
            rel = path.relative_to(layers.resolve())
        except ValueError:
            unexpected.append(finding); continue
        row = known.get((path.name, member))
        location = (len(rel.parts) == 7 and rel.parts[0].isdigit()
                    and rel.parts[1:6] == ('usr', 'share', 'doc', 'controlplane-api', 'debian-sources'))
        coordinate = [finding['StartLine'], finding['EndLine']]
        if (not location or not separator or path.name not in archives or not row
                or coordinate not in row['rules'].get(finding['RuleID'], [])):
            unexpected.append(finding); continue
        if path not in verified:
            with path.open('rb') as stream:
                verified[path] = hashlib.file_digest(stream, 'sha256').hexdigest() == archives[path.name]['sha256']
        if verified[path]:
            accepted += 1
        else:
            unexpected.append(finding)
    return accepted, unexpected
