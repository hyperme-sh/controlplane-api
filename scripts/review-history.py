"""Export reachable Git objects for static scanning; never execute old code."""
import json
from pathlib import Path
import subprocess
import sys


def git(*args):
    return subprocess.check_output(['git', *args])


def review(output):
    if git('rev-parse', '--is-shallow-repository').strip() != b'false':
        raise ValueError('Full history required')
    refs = dict(line.split(' ', 1) for line in git('for-each-ref', '--format=%(refname) %(objectname)', 'refs/remotes/origin', 'refs/tags').decode().splitlines())
    refs['HEAD'] = git('rev-parse', 'HEAD').decode().strip()
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for line in git('rev-list', '--objects', *sorted(set(refs.values()))).decode().splitlines():
        oid, _, path = line.partition(' ')
        kind = git('cat-file', '-t', oid).decode().strip()
        if kind not in ('blob', 'commit', 'tag'):
            continue
        data = git('cat-file', kind, oid)
        # Keep archive suffixes so recursive archive inspection can recognize them.
        suffix = ''.join(Path(path).suffixes) if path.endswith(('.whl', '.zip', '.tar.gz', '.tgz')) else '.txt'
        (output/(oid+suffix)).write_bytes(data)
        rows.append({'object': oid, 'kind': kind, 'path': path})
    print(json.dumps({'refs': refs, 'objects': rows, 'publication_cleared': False,
        'scope': 'Reachable HEAD and fetched origin branches/tags; no hidden/deleted refs, remote LFS content or other repositories'}, sort_keys=True))


if __name__ == '__main__':
    review(Path(sys.argv[1]))
