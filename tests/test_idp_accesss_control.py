from functools import partial

import pytest
from webdriver_recorder.browser import Chrome

from tests.helpers import CTRL_KEY, Locators, WebTestUtils
from tests.models import ServiceProviderInstance, AccountNetid, TestSecrets


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
def netid() -> str:
    return AccountNetid.sptest01.value


@pytest.fixture
def netid03() -> str:
    return AccountNetid.sptest03.value


@pytest.fixture
def netid06() -> str:
    return AccountNetid.sptest06.value


@pytest.fixture
def netid07() -> str:
    return AccountNetid.sptest07.value


@pytest.fixture
def netid08() -> str:
    return AccountNetid.sptest08.value


@pytest.fixture
def netid04() -> str:
    return AccountNetid.sptest04.value


def test_auto_2fa(browser, netid03, utils, sp_url, secrets, sp_domain, new_tab):
    """
    AC-1	Auto 2FA	diafine7, sptest03
    a. Start new pwd session at https://diafine7.sandbox.iam.s.uw.edu/shibprod. Close browser.
    b. Start pwd SSO session at https://diafine6.sandbox.iam.s.uw.edu/shibprod.
        Use SSO to access https://diafine7.sandbox.iam.s.uw.edu/shibprod. Close browser.
    """

    # a
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine7
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibprod')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid03, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Use your 2fa device')
        fresh_browser.close()

    # b
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibprod')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid03, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        new_tab()
        sp = ServiceProviderInstance.diafine7
        fresh_browser.get(f'{sp_url(sp)}/shibprod')
        fresh_browser.wait_for_tag('p', 'Use your 2fa device')
