import os
from typing import Callable
import inflection

import pytest

from tests.secret_manager import SecretManager
from tests.helpers import WebTestUtils, load_settings
from tests.models import WebTestSettings, TestOptions, ServiceProviderInstance, TestSecrets


def pytest_addoption(parser):
    parser.addoption('--settings-file', default='settings.yaml',
                     help="Use this if you want to provide a settings YAML file yourself.")
    parser.addoption('--settings-profile', default='base',
                     help="Use this if you want to use settings from a specific root node of the settings file.")
    for field, f_config in TestOptions.__fields__.items():
        option_name = f'--{inflection.dasherize(field)}'
        help_text = f_config.field_info.description
        option_default = f_config.default
        option_type = f_config.type_
        kwargs = dict(default=option_default, help=help_text)
        if option_type is bool:
            action = 'store_false' if option_default is True else 'store_true'
            kwargs['action'] = action

        parser.addoption(option_name, **kwargs)


@pytest.fixture(scope='session')
def settings(request) -> WebTestSettings:
    filename = request.config.getoption('--settings-file')
    settings_env = request.config.getoption('--settings-profile')
    return load_settings(filename, settings_env, option_overrides=TestOptions.parse_overrides(request.config))


@pytest.fixture(scope='session')
def utils(settings: WebTestSettings) -> WebTestUtils:
    return WebTestUtils(settings)


@pytest.fixture(scope='session', autouse=True)
def manage_test_service_providers(settings, utils):
    if not settings.test_options.skip_test_service_provider_start:
        utils.sp_aws_operations.start_instances()
        utils.sp_aws_operations.update_instance_a_records()
        utils.sp_aws_operations.wait_for_ip_propagation()
    yield
    if not settings.test_options.skip_test_service_provider_stop:
        utils.sp_aws_operations.stop_instances()


@pytest.fixture(autouse=True)
def report_test(report_test):
    """Re-wraps with autouse=True so that reports are always generated."""
    return report_test


@pytest.fixture
def sp_url(utils) -> Callable[[ServiceProviderInstance], str]:
    """Convenience fixture to make this less unwieldy to include in f-strings."""
    return utils.service_provider_url

@pytest.fixture
def sp_domain(utils) -> Callable[[ServiceProviderInstance], str]:
    return utils.service_provider_domain


@pytest.fixture
def secret_manager(settings):
    return SecretManager(settings.secret_manager)


@pytest.fixture
def secrets(secret_manager) -> TestSecrets:
    return secret_manager.get_secret_data(model_type=TestSecrets)
