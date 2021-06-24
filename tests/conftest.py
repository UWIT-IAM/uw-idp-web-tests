import os
from typing import Callable
import inflection

import pytest
from tests.helpers import Locators


from tests.secret_manager import SecretManager
from tests.helpers import WebTestUtils, load_settings, CTRL_KEY
from tests.models import WebTestSettings, TestOptions, ServiceProviderInstance, TestSecrets, AccountNetid
from webdriver_recorder.browser import Chrome


def pytest_addoption(parser):
    parser.addoption('--settings-file', default='settings.yaml',
                     help="Use this if you want to provide a settings YAML file yourself.")
    parser.addoption('--settings-profile', default='base',
                     help="Use this if you want to use settings from a specific root node of the settings file.")
    parser.addoption("--env", action="store", default="prod", help="Use this is you want to set the test environment "
                                                                   "to eval or prod. Default environment is prod. "
                                                                   "Usage: --env=eval or --env=prod")
    for field, f_config in TestOptions.__fields__.items():
        option_name = f'--{inflection.dasherize(field)}'
        help_text = f_config.field_info.description
        if not f_config.field_info.extra.get('add_cli_arg', True):
            continue
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
def report_title(settings) -> str:
    return settings.test_options.report_title


@pytest.fixture(scope='session')
def utils(settings: WebTestSettings, secrets: TestSecrets) -> WebTestUtils:
    return WebTestUtils(settings, secrets)


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


@pytest.fixture(scope='session')
def test_env(request):
    """
    Determines which environment the tests are run against, prod or eval. Prod is the default.
    """
    return request.config.getoption("--env")


@pytest.fixture
def browser() -> Chrome:
    return Chrome()


@pytest.fixture(scope='class')
def class_browser() -> Chrome:
    browser = Chrome()
    try:
        yield browser
    finally:  # Even if there is an error
        browser.close()


@pytest.fixture
def new_tab(browser):
    def inner():
        browser.execute_script("window.open('');")
        browser.switch_to.window(browser.window_handles[-1])
    return inner


@pytest.fixture
def close_tab(browser):
    def inner():
        browser.find_element_by_tag_name('body').send_keys(CTRL_KEY + 'w')
    return inner


@pytest.fixture
def netid() -> str:
    return AccountNetid.sptest01.value


@pytest.fixture
def netid2() -> str:
    return AccountNetid.sptest02.value


@pytest.fixture
def netid3() -> str:
    return AccountNetid.sptest03.value


@pytest.fixture
def netid4() -> str:
    return AccountNetid.sptest04.value


@pytest.fixture
def netid5() -> str:
    return AccountNetid.sptest05.value


@pytest.fixture
def netid6() -> str:
    return AccountNetid.sptest06.value


@pytest.fixture
def netid7() -> str:
    return AccountNetid.sptest07.value


@pytest.fixture
def netid8() -> str:
    return AccountNetid.sptest08.value


@pytest.fixture
def netid10() -> str:
    return AccountNetid.sptest10.value


@pytest.fixture
def clean_browser(browser: Chrome) -> Chrome:
    browser.delete_all_cookies()
    return browser


@pytest.fixture
def two_fa_submit_form(secrets):
    def inner(current_browser):
        current_browser.wait_for_tag('p', 'Use your 2FA device.')
        current_browser.switch_to.frame(current_browser.find_element_by_id('duo_iframe'))
        current_browser.execute_script("document.getElementById('passcode').click()")
        passcode = secrets.test_accounts.duo_code
        current_browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]", passcode)
        current_browser.snap()
        current_browser.execute_script("document.getElementById('passcode').click()")
    return inner


@pytest.fixture
def login_submit_form():
    def inner(current_browser, netid, password):
        """
        Accepts a running browser session, a netid and password
        """
        current_browser.wait_for_tag('p', 'Please sign in.')
        current_browser.send_inputs(netid, password)
        current_browser.click(Locators.submit_button)
    return inner


