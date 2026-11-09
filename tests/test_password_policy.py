import pytest

from controlplane_api.exceptions import InvalidOperationException
from controlplane_api.utils import validate_password


@pytest.mark.parametrize("password", ["Aa1!aaaa", "12345678aB&"])
def test_valid_password_is_returned_unchanged(password):
    assert validate_password(password) == password


@pytest.mark.parametrize("password", [
    "Aa1!", "Aa1!aaa", "Aa1!aaaa#", "Aa1!aaaa\n", "aaaaaaaa!1",
    "AAAAAAAA!1", "Aaaaaaaa!", "Aaaaaaaa1",
])
def test_rejects_password_outside_policy(password):
    with pytest.raises(InvalidOperationException):
        validate_password(password)
