"""Check credential isolation without network or dependency installation."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/anonymous-command.sh'


def test_inherited_credentials_and_caches_are_removed(tmp_path):
    env = dict(os.environ, GH_TOKEN='not-a-real-token', GITHUB_TOKEN='not-a-real-token',
               GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='http.extraheader',
               GIT_CONFIG_VALUE_0='secret', UV_CACHE_DIR=str(tmp_path),
               UV_INDEX_URL='https://private.invalid', SSH_AUTH_SOCK='/private/socket')
    result = subprocess.run(
        ['bash', str(SCRIPT), sys.executable, '-c',
         'import json, os; print(json.dumps(dict(os.environ)))'],
        env=env, text=True, capture_output=True, check=True)
    child = json.loads(result.stdout)
    for key in ('GH_TOKEN', 'GITHUB_TOKEN', 'GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0',
                'UV_INDEX_URL', 'SSH_AUTH_SOCK'):
        assert key not in child
    assert child['GIT_CONFIG_GLOBAL'] == '/dev/null'
    assert child['GIT_CONFIG_NOSYSTEM'] == '1'
    assert child['GIT_CONFIG_COUNT'] == '0'
    assert child['GIT_TERMINAL_PROMPT'] == '0'
    assert child['UV_CACHE_DIR'] != str(tmp_path)
    assert not Path(child['HOME']).exists()


def test_failure_status_and_cleanup():
    result = subprocess.run(['bash', str(SCRIPT), 'bash', '-c',
                             'echo "$HOME"; exit 17'], text=True, capture_output=True)
    assert result.returncode == 17
    assert not Path(result.stdout.strip()).exists()


def test_command_required():
    result = subprocess.run(['bash', str(SCRIPT)], capture_output=True)
    assert result.returncode == 2
