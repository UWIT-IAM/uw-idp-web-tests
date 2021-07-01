import copy
import logging
from typing import Callable, NoReturn, Optional

import inflection
import pytest
from webdriver_recorder.browser import BrowserRecorder, Chrome, Remote

from tests.helpers import Locators, WebTestUtils, load_settings
from tests.models import AccountNetid, ServiceProviderInstance, TestOptions, TestSecrets, WebTestSettings
from tests.secret_manager import SecretManager


def pytest_addoption(parser):
    parser.addoption('--settings-file', default='settings.yaml',
                     help="Use this if you want to provide a settings YAML file yourself.")
    parser.addoption('--settings-profile', default='base',
                     help="Use this if you want to use settings from a specific root node of the settings file.")
    parser.addoption('--reuse-chromedriver', default=4444,
                     help="Where possible, the test suite will try to reuse a single chromedriver connection."
                          "If you can't or don't want to use the default port for this, you may set a different port "
                          "with this option.")
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
def chrome_options(chrome_options):
    chrome_options.add_argument('disable-extensions')
    chrome_options.add_argument('disable-crash-reporter')
    return chrome_options


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
        logging.info("Starting all test service provider instances.")
        utils.sp_aws_operations.start_instances()
        utils.sp_aws_operations.update_instance_a_records()
        utils.sp_aws_operations.wait_for_ip_propagation()
    else:
        logging.info("Service provider instances will be started as-needed.")
    try:
        yield
    finally:
        if not settings.test_options.skip_test_service_provider_stop:
            logging.info("Stopping all test service provider instances.")
            utils.sp_aws_operations.stop_instances()
        else:
            logging.info("Leaving all active test service provider instances running.")


@pytest.fixture(scope='session')
def sp_url(utils) -> Callable[[ServiceProviderInstance], str]:
    """Convenience fixture to make this less unwieldy to include in f-strings."""
    return utils.service_provider_url


@pytest.fixture(scope='session')
def sp_domain(utils) -> Callable[[ServiceProviderInstance], str]:
    return utils.service_provider_domain


@pytest.fixture(scope='session')
def sp_shib_url(test_env, sp_url) -> Callable[..., NoReturn]:
    """
    fixture function that returns the provided SP's shibboleth URL.
    Requires the service_provider parameter.

    Accepts an optional parameter, 'append', which you can set to append
    any string such as 'force', 'mfa', etc.
    """

    def inner(service_provider: ServiceProviderInstance, append: str = ''):
        url = sp_url(service_provider)
        url += f'/shib{test_env}{append}'
        return url

    return inner


@pytest.fixture(scope='session')
def secret_manager(settings):
    return SecretManager(settings.secret_manager)


@pytest.fixture(scope='session')
def secrets(secret_manager) -> TestSecrets:
    return secret_manager.get_secret_data(model_type=TestSecrets)


@pytest.fixture(scope='session')
def test_env(request):
    """
    Determines which environment the tests are run against, prod or eval. Prod is the default.
    """
    return request.config.getoption("--env")


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
def enter_duo_passcode(secrets, sp_domain) -> Callable[..., NoReturn]:
    default_passcode = secrets.test_accounts.duo_code.get_secret_value()

    def inner(
            current_browser: Chrome,
            passcode: str = default_passcode,
            select_iframe: bool = True,
            assert_success: Optional[bool] = None,
            assert_failure: Optional[bool] = None,
            match_service_provider: Optional[ServiceProviderInstance] = None,
    ):
        """
        :param current_browser: The browser you want to invoke these actions on.
        :param passcode: The passcode you want to enter; if not provided, will use the
            correct test instance passcode.
        :param select_iframe: Defaults to True;
                              you can toggle this to False if you are already in an iframe context.
        :param assert_success: Optional. Will ensure that the result was a successful
                               sign in attempt. If not overridden, will default to True
                               if the passcode being entered is the correct passcode.
        :param assert_failure: Optional. Will ensure that the result was a failed
                               sign in attempt. If not overridden with a bool, will
                               default to True if the passcode being entered is
                               not the correct passcode.
        :param match_service_provider: Optional[ServiceProviderInstance]:
                                 The SP you expect to find in the 'assert_success'
                                 case output. If not provided, only the generic success
                                 message will be matched.
                                 (Providing this gives your tests a higher confidence.)
        """

        passcode_matches_default = passcode == default_passcode

        if assert_success is None:
            assert_success = passcode_matches_default

        if assert_failure is None:
            assert_failure = not passcode_matches_default

        if select_iframe:
            current_browser.wait_for_tag('p', 'Use your 2FA device.')
            iframe = current_browser.wait_for(Locators.iframe)
            current_browser.switch_to.frame(iframe)
            current_browser.wait_for(Locators.passcode_button)
            current_browser.execute_script("document.getElementById('passcode').click();")

        current_browser.execute_script(
            "document.getElementsByClassName('passcode-input')[0].value = arguments[0];",
            passcode
        )
        current_browser.snap()
        current_browser.execute_script("document.getElementById('passcode').click();")

        if assert_success:
            current_browser.switch_to.default_content()
            sp = sp_domain(match_service_provider) if match_service_provider else ''
            current_browser.wait_for_tag('h2', f'{sp} sign-in success!')
        elif assert_failure:
            current_browser.wait_for_tag('span', 'Incorrect passcode. Enter a passcode from Duo Mobile.')

    return inner


@pytest.fixture(scope='session')
def log_in_netid(secrets: TestSecrets, sp_domain) -> Callable[..., NoReturn]:
    default_password = secrets.test_accounts.password.get_secret_value()

    def inner(current_browser: Chrome, netid: str, password: Optional[str] = default_password,
              assert_success: Optional[bool] = None, match_service_provider: Optional[ServiceProviderInstance] = None):
        """
        Accepts a running browser session, a netid and password
        """
        if assert_success is None:
            assert_success = password == default_password
        match_service_provider = sp_domain(match_service_provider) if match_service_provider else ''
        current_browser.wait_for_tag('p', 'Please sign in.')
        current_browser.send_inputs(netid, password)
        current_browser.click(Locators.submit_button)
        if assert_success:
            current_browser.wait_for_tag('h2', f'{match_service_provider} sign-in success!')
    return inner


@pytest.fixture(scope='session')
def get_fresh_browser(selenium_server, chrome_options, request) -> Callable[..., BrowserRecorder]:
    """
    This is a fixture function that creates a fresh browser instance
    based on the current environment configuration.

        def test_the_thing(get_fresh_browser: Callable[None, BrowserRecorder]):
            browser = get_fresh_browser()

    You manage the scope of this browser; you should always make sure to
    wrap the browser use in a try/finally block to call `quit()` on
    the browser instance in all cases.

    Note that only the function is session-scoped (so that all scopes can use it);
    the instance created by the function is self-contained and will share the scope of
    whatever test/fixture calls it.

    For local (`Chrome`) instances, we add the 'detach' option in order to
    reuse a single chromedriver instance, which speeds things up a bit.
    """
    options = copy.deepcopy(chrome_options)
    options.add_experimental_option('detach', True)  # See docstring above
    args = dict(options=options)
    if selenium_server and selenium_server.strip():
        browser_cls = Remote
        args['command_executor'] = f'http://{selenium_server}/wd/hub'
    else:
        browser_cls = Chrome
        # Reuse a single local instance for the duration of the tests.
        args['port'] = request.config.getoption('--reuse-chromedriver')

    return lambda: browser_cls(**args)


@pytest.fixture(scope='class')
def fresh_class_browser(get_fresh_browser, request):
    request.cls.browser = get_fresh_browser()
    try:
        yield
    finally:
        request.cls.browser.quit()


@pytest.fixture
def fresh_browser(get_fresh_browser):
    browser = get_fresh_browser()
    try:
        yield browser
    finally:
        browser.quit()
