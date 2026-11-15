import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_base import verify_layers, verify, digest


def test_base_prefix_allows_consumer_layers_but_refuses_changed_base():
    m={'diff_ids':['a','b']}
    verify_layers({'rootfs':{'diff_ids':['a','b','c']}},m)
    with pytest.raises(ValueError):verify_layers({'rootfs':{'diff_ids':['a','x']}},m)


def test_changed_base_inventory_refuses_before_source_read(tmp_path):
    p=tmp_path/'var/lib/dpkg/status';p.parent.mkdir(parents=True);p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='inventory'):
        verify(tmp_path,{'publication_cleared':False,'status_sha256':digest(b'original')},tmp_path)


def test_legal_path_escape_refuses(tmp_path):
    p=tmp_path/'var/lib/dpkg/status';p.parent.mkdir(parents=True);p.write_bytes(b'status')
    m={'publication_cleared':False,'status_sha256':digest(b'status'),'legal_sha256':{'../outside':'x'}}
    with pytest.raises(ValueError,match='legal'):
        verify(tmp_path,m,tmp_path)
