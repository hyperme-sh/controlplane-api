import os
from pathlib import Path
import stat

import pytest
from controlplane_api import audit_files


@pytest.fixture(autouse=True)
def private_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_files.tempfile, 'gettempdir', lambda: str(tmp_path))


@pytest.mark.parametrize('name', ['/tmp/escape', '../escape', 'a/b', r'a\b', '..', '', 'a\x00b'])
def test_rejects_paths_before_creating_directory(name, tmp_path):
    with pytest.raises(ValueError):
        audit_files.temp_path(name)
    assert list(tmp_path.iterdir()) == []


def test_path_lookup_keeps_existence_check_semantics():
    path = audit_files.temp_path('seed.lock')
    assert not path.exists()
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700


def test_append_and_read_use_private_regular_files():
    with audit_files.open_file('unit.jsonl', append=True) as stream:
        stream.write('first\n')
    with audit_files.open_file('unit.jsonl', append=True) as stream:
        stream.write('second\n')
    with audit_files.open_file('unit.jsonl') as stream:
        assert stream.read() == 'first\nsecond\n'
    assert stat.S_IMODE(audit_files.temp_path('unit.jsonl').stat().st_mode) == 0o600


def test_symlink_and_hardlink_targets_are_untouched(tmp_path):
    target = tmp_path/'outside'
    target.write_text('unchanged')
    target.chmod(0o600)
    root = audit_files.directory()
    for name, link in [('symbolic', True), ('hard', False)]:
        path = root/name
        path.symlink_to(target) if link else os.link(target, path)
        with pytest.raises((ValueError, OSError)):
            with audit_files.open_file(name, append=True) as stream:
                stream.write('bad')
    assert target.read_text() == 'unchanged'


def test_directory_symlink_and_public_permissions_refused(tmp_path):
    root = tmp_path/f'controlplane-api-{os.geteuid()}'
    root.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError):
        audit_files.directory()
    root.unlink()
    root.mkdir(mode=0o755)
    with pytest.raises(ValueError):
        audit_files.directory()


def test_fifo_refused_without_blocking():
    root = audit_files.directory()
    os.mkfifo(root/'pipe', mode=0o600)
    with pytest.raises((OSError, ValueError)):
        with audit_files.open_file('pipe'):
            pass


def test_tenant_globs_and_paths_are_rejected():
    for tenant in ('../other', '*', 'a/b', 'a\\b'):
        with pytest.raises(ValueError):
            audit_files.log_paths(tenant)


def test_log_listing_is_tenant_and_date_scoped():
    root = audit_files.directory()
    for name in ('audit_logs_forone_20261112.jsonl', 'audit_logs_fortwo_20261112.jsonl', 'audit_logs_forone_notes.jsonl'):
        with audit_files.open_file(name, append=True):
            pass
    assert audit_files.log_paths('one') == [root/'audit_logs_forone_20261112.jsonl']


def test_capture_writes_only_private_tenant_log():
    import asyncio
    from controlplane_api.dtos.audit import AuditLogDto
    from controlplane_api.utils import capture_audit_log
    asyncio.run(capture_audit_log(AuditLogDto(entity='unit', action='read', tenant_id='tenant-one')))
    paths = audit_files.log_paths('tenant-one')
    assert len(paths) == 1
    with audit_files.open_file(paths[0].name) as stream:
        assert 'tenant-one' in stream.read()
    with pytest.raises(ValueError):
        asyncio.run(capture_audit_log(AuditLogDto(entity='unit', action='read', tenant_id='../escape')))
