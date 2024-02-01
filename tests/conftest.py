import copy
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Callable, NoReturn, Optional

import pytest
from webdriver_recorder.browser import BrowserRecorder, Chrome, Remote

from tests.helpers import Locators, WebTestUtils, load_settings
from tests.models import AccountNetid, ServiceProviderInstance, TestOptions, TestSecrets, WebTestSettings
from tests.secret_manager import SecretManager


def pytest_addoption(parser):
    group = parser.getgroup('idp_tests')
    group.addoption('--settings-file', default='settings.yaml',
                     help="Use this if you want to provide a settings YAML file yourself.")
    group.addoption('--settings-profile', default='base',
                     help="Use this if you want to use settings from a specific root node of the settings file.")
    group.addoption('--lb-num-loops', default=0,
                    help="If set to a number greater than 0, "
                         "the test_generate_requests.py test will make IdP requests the given number of times.")
    group.addoption('--lb-sleep-time', default=60,
                    help="The number of seconds to sleep between login attempts when running login request "
                         "generator.")

    TestOptions.apply_to_parser(group)


@pytest.fixture(scope='session')
def selenium_server(settings) -> str:
    return settings.test_options.selenium_server


@pytest.fixture(scope='session')
def settings(request) -> WebTestSettings:
    filename = request.config.getoption('--settings-file')
    settings_env = request.config.getoption('--settings-profile')
    test_options = TestOptions.parse_overrides(request.config)
    settings = load_settings(filename, settings_env, option_overrides=test_options)
    logging.debug(f'Derived settings: {settings.dict()}')
    return settings


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
        record_sets = utils.sp_aws_operations.record_sets
        service_providers = utils.sp_aws_operations.service_providers.keys()
        service_providers = [
            sp for sp in service_providers if
            utils.sp_aws_operations.dns_record_requires_update(record_sets, sp)
        ]
        if service_providers:
            utils.sp_aws_operations.update_instance_a_records(*service_providers)
            utils.sp_aws_operations.wait_for_ip_propagation(*service_providers)
    else:
        logging.info("Service provider instances will be started as-needed.")


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
def test_env(settings):
    """
    Determines which environment the tests are run against, prod or eval. Prod is the default.
    """
    env = settings.test_options.env
    logging.info(f"Testing against {env} idp stack")
    return env


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
def enter_duo_passcode_2(secrets, sp_domain, test_env) -> Callable[..., NoReturn]:
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

        wait = WebDriverWait(current_browser, 10)
        print('1')
        element = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                         "//input[contains(@id, 'passcode-input')]")))
        print('1_a')
        current_browser.snap()
        print(f'_input value--------------->{element.get_attribute("value")}')
        # Click the element
        element.click()
        current_browser.execute_script("arguments[0].value = '';", element)
        current_browser.snap()
        current_browser.send_inputs(passcode)
        print('2_')
        current_browser.snap()
        current_browser.wait_for_tag('button', 'Verify').click()

        current_browser.snap()

        if assert_success:
            if test_env == 'prod':
                current_browser.switch_to.default_content()
            sp = sp_domain(match_service_provider) if match_service_provider else ''
            current_browser.wait_for_tag('h2', f'{sp} sign-in success!')
        elif assert_failure:
            wait = WebDriverWait(current_browser, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Invalid passcode.')]")))

    return inner


@pytest.fixture
def enter_duo_passcode(secrets, sp_domain, test_env) -> Callable[..., NoReturn]:
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

        if select_iframe and test_env == 'prod':
            current_browser.wait_for_tag('p', 'Use your 2FA device.')
            iframe = current_browser.wait_for(Locators.iframe)
            current_browser.switch_to.frame(iframe)
            current_browser.wait_for(Locators.passcode_button)
            current_browser.execute_script("document.getElementById('passcode').click();")

        if test_env == 'prod':
            current_browser.execute_script(
                "document.getElementsByClassName('passcode-input')[0].value = arguments[0];",
                passcode
            )
            current_browser.snap()
            current_browser.execute_script("document.getElementById('passcode').click();")

        if select_iframe and test_env == 'eval':
            current_browser.wait_for_tag('a', 'Other options').click()
            current_browser.wait_for_tag('b', 'Other options to log in')
        wait = WebDriverWait(current_browser, 10)
        print('1')
        element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'Bypass code') and "
                                                                         "contains( "
                                                               "@class, 'row') and contains(@class, 'display-flex') ]"))
                             )
        # element = wait.until(EC.element_to_be_clickable((By.XPATH,
        #                                                  "//input[contains(@id, 'passcode-input')]")))
        print('1a')
        current_browser.snap()
        print(f'input value--------------->{element.get_attribute("value")}')
        # Click the element
        element.click()
        current_browser.snap()
        current_browser.send_inputs(passcode)
        print('2')
        current_browser.snap()
        current_browser.wait_for_tag('button', 'Verify').click()

        current_browser.snap()

        if assert_success:
            if test_env == 'prod':
                current_browser.switch_to.default_content()
            sp = sp_domain(match_service_provider) if match_service_provider else ''
            current_browser.wait_for_tag('h2', f'{sp} sign-in success!')
        elif assert_failure:
            wait = WebDriverWait(current_browser, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Invalid passcode.')]")))

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
def get_fresh_browser(selenium_server, chrome_options, settings) -> Callable[..., BrowserRecorder]:
    """
    This is a fixture function that creates a fresh browser instance
    based on the current environment configuration.

    Before you use this fixture directly, make sure the `browser` fixture
    doesn't already do what you need.

    If you call this function directly, you manage the scope of this browser
    instance; you must make sure to wrap the browser use in a try/finally
    block to call `quit()` on the browser instance in all cases.

    Note that only the function is session-scoped (so that all scopes can use it);
    the instance created by the function is self-contained and will share the scope of
    whatever test/fixture calls it.

    For local (`Chrome`) instances, we add the 'detach' option in order to
    reuse a single chromedriver instance, which speeds things up a bit.
    """
    options = copy.deepcopy(chrome_options)
    args = dict(options=options)
    if selenium_server and selenium_server.strip():
        browser_cls = Remote
        args['command_executor'] = f'http://{selenium_server}/wd/hub'
    else:
        browser_cls = Chrome
        options.add_experimental_option('detach', True)
        args['port'] = settings.test_options.reuse_chromedriver
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


@pytest.fixture()
def skip_if_eval(test_env):
    if test_env == 'eval':
        pytest.skip(msg='skipped test, we are in eval.')
