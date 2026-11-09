"""Reject the issue-16 deprecations in source and isolated installed tests."""
import warnings


def pytest_configure(config):
    warnings.filterwarnings('error', message='Using extra keyword arguments on `Field` is deprecated',
                            category=DeprecationWarning, module=r'controlplane_api\.dtos\.health')
    warnings.filterwarnings('error', message='Using `httpx` with `starlette.testclient` is deprecated',
                            category=DeprecationWarning)
