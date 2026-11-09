import copy
import importlib.util
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from qualify_health_metadata import prove


def transition():
    before = json.loads((ROOT / 'releases/candidate/contract.json').read_text())
    definition = json.loads((ROOT / 'compatibility/health-field-metadata.json').read_text())
    after = copy.deepcopy(before)
    after['packaged_file_sha256'][definition['runtime_path']] = definition['after_sha256']
    return before, after, definition, copy.deepcopy(definition['dist_info_sha256'])


def test_exact_reviewed_transition_preserves_other_runtime_and_installer_bytes():
    prove(*transition())


@pytest.mark.parametrize('change', ['other-runtime', 'health', 'inventory', 'installer', 'coverage'])
def test_unreviewed_compatibility_changes_refuse(change):
    before, after, definition, installer = transition()
    if change == 'other-runtime':
        key = next(k for k in after['packaged_file_sha256'] if k != definition['runtime_path'])
        after['packaged_file_sha256'][key] = 'f' * 64
    if change == 'health': after['packaged_file_sha256'][definition['runtime_path']] = 'f' * 64
    if change == 'inventory': after['packaged_file_sha256']['controlplane_api/extra.py'] = 'f' * 64
    if change == 'installer': installer['METADATA'] = 'f' * 64
    if change == 'coverage': after['coverage'] = 'partial'
    with pytest.raises(ValueError): prove(before, after, definition, installer)
