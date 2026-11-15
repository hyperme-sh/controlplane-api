from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from classify_base_fingerprint import known, FINGERPRINT
from container_audit import check_member

def test_fingerprint_exception_is_exact(tmp_path):
    row = {'File': str(tmp_path / 'image-config.json'), 'RuleID': 'generic-api-key', 'Secret': FINGERPRINT}
    assert known(row, tmp_path)
    for field, value in [('File', str(tmp_path/'runtime.py')), ('Secret', FINGERPRINT+'x'), ('RuleID', 'private-key')]:
        assert not known(dict(row, **{field: value}), tmp_path)

@pytest.mark.parametrize('path,data', [('stripe/__init__.py', b''), ('controlplane_api/a.py', b'import stripe'), ('x.dist-info/METADATA', b'Requires-Dist: payment-service')])
def test_hosted_implementation_refused(path, data):
    with pytest.raises(ValueError):
        check_member(path, data)
