"""Private, descriptor-checked temporary audit storage."""
from contextlib import contextmanager
import os
from pathlib import Path
import re
import stat
import tempfile

_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,199}\Z')
_TENANT = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z')


def directory() -> Path:
    root = Path(tempfile.gettempdir()) / f'controlplane-api-{os.geteuid()}'
    try:
        root.mkdir(mode=0o700)
    except FileExistsError:
        pass
    meta = root.lstat()
    if not stat.S_ISDIR(meta.st_mode) or meta.st_uid != os.geteuid() or stat.S_IMODE(meta.st_mode) != 0o700:
        raise ValueError('Untrusted audit directory')
    return root


def _filename(name: str) -> str:
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise ValueError('A simple temporary filename is required')
    return name


def _file(meta):
    if (not stat.S_ISREG(meta.st_mode) or meta.st_uid != os.geteuid()
            or stat.S_IMODE(meta.st_mode) != 0o600 or meta.st_nlink != 1):
        raise ValueError('Untrusted audit file')


def temp_path(name: str) -> Path:
    """Return a private path without creating it (callers also use existence checks)."""
    name = _filename(name)
    path = directory()/name
    try:
        _file(path.lstat())
    except FileNotFoundError:
        pass
    return path


def tenant_prefix(tenant_id: str | None) -> str:
    tenant = tenant_id if tenant_id else 'host'
    if not isinstance(tenant, str) or not _TENANT.fullmatch(tenant):
        raise ValueError('Unsafe audit tenant identifier')
    return 'audit_logs_for'+tenant+'_'


@contextmanager
def open_file(name: str, *, append=False):
    name = _filename(name)
    root = directory()
    directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        meta = os.fstat(directory_fd)
        if meta.st_uid != os.geteuid() or stat.S_IMODE(meta.st_mode) != 0o700:
            raise ValueError('Untrusted audit directory')
        flags = os.O_NOFOLLOW | os.O_NONBLOCK
        flags |= os.O_WRONLY | os.O_APPEND | os.O_CREAT if append else os.O_RDONLY
        fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
        try:
            _file(os.fstat(fd))
            stream = os.fdopen(fd, 'a' if append else 'r', encoding='utf-8')
        except BaseException:
            os.close(fd)
            raise
        with stream:
            yield stream
    finally:
        os.close(directory_fd)


def log_paths(tenant_id: str | None = None) -> list[Path]:
    prefix = tenant_prefix(tenant_id)
    return sorted(path for path in directory().iterdir()
                  if re.fullmatch(re.escape(prefix)+r'[0-9]{8}\.jsonl', path.name))
