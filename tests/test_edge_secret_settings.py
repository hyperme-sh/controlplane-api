"""Opt-in service startup guard and compatible rotation settings."""
import logging
import secrets
import pytest
from controlplane_api.config import Settings, _PUBLISHED_API_KEY_SECRETS

CURRENT = 'API_KEY_EXCHANGE_JWT_SECRET'
INTERNAL = 'API_KEYS_INTERNAL_TOKEN'


def valid(**overrides):
    values = {CURRENT: secrets.token_hex(24), INTERNAL: secrets.token_hex(24)}
    return Settings(_env_file=None, **(values | overrides))


@pytest.mark.parametrize('name', [CURRENT, INTERNAL, CURRENT+'_PREVIOUS', INTERNAL+'_PREVIOUS'])
@pytest.mark.parametrize('bad', ['', 'x'*31, *_PUBLISHED_API_KEY_SECRETS,
    'dev-'+'x'*48, 'laptop-'+'x'*48, 'replace-with'+'x'*48])
def test_weak_values_refused_without_disclosure(name, bad, caplog):
    if name.endswith('_PREVIOUS') and not bad:
        valid(**{name:bad}).require_edge_secrets()
        return  # Optional previous values default to empty.
    settings=valid(**{name:bad})
    with pytest.raises(ValueError, match=name) as caught:
        settings.require_edge_secrets()
    with caplog.at_level(logging.ERROR):
        logging.getLogger(__name__).error('Startup refused: %s', caught.value)
    if bad:
        assert bad not in str(caught.value)
        assert bad not in caplog.text
        assert bad not in repr(settings)


def test_defaults_strict_and_explicit_opt_out():
    with pytest.raises(ValueError, match=CURRENT):
        Settings(_env_file=None, **{CURRENT:'', INTERNAL:''}).require_edge_secrets()
    Settings(_env_file=None, EDGE_SECRETS_REQUIRED=False, **{CURRENT:'', INTERNAL:''}).require_edge_secrets()
    valid().require_edge_secrets()


@pytest.mark.parametrize('target', [INTERNAL, CURRENT+'_PREVIOUS', INTERNAL+'_PREVIOUS'])
def test_reused_secrets_refused(target):
    value=secrets.token_hex(24)
    with pytest.raises(ValueError, match=target):
        valid(**{CURRENT:value, target:value}).require_edge_secrets()


def test_rotation_order_and_no_previous_promotion():
    current, previous, token, old_token = [secrets.token_hex(24) for _ in range(4)]
    settings=valid(**{CURRENT:current, INTERNAL:token, CURRENT+'_PREVIOUS':previous, INTERNAL+'_PREVIOUS':old_token})
    settings.require_edge_secrets()
    assert settings.usable_api_key_exchange_secrets() == (current,previous)
    assert settings.usable_api_keys_internal_tokens() == (token,old_token)
    assert settings.usable_api_key_exchange_secret() == current
    assert settings.usable_api_keys_internal_token() == token
    assert valid(**{CURRENT:'', CURRENT+'_PREVIOUS':previous}).usable_api_key_exchange_secrets() == (None,previous)
