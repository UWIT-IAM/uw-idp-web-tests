from functools import partial
from typing import Callable

import pytest
from webdriver_recorder.browser import Chrome

from tests.helpers import CTRL_KEY, Locators, WebTestUtils
from tests.models import ServiceProviderInstance, AccountNetid, TestSecrets


@pytest.fixture
def browser() -> Chrome:
    return Chrome()


@pytest.fixture
def new_tab(browser):
    def inner():
        browser.find_element_by_tag_name('body').send_keys(CTRL_KEY + 't')
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
def clean_browser(browser: Chrome) -> Chrome:
    browser.delete_all_cookies()
    return browser


def add_suffix(suffix: str, netid: str) -> str:
    return f'{netid}{suffix}'


def crazy_casing(netid: str) -> str:
    letters = list(netid)
    for i, letter in enumerate(letters):
        if i % 2 == 0:
            letters[i] = letter.upper()
    return ''.join(letters)


# PWD 1–4, 6–8, 10
@pytest.mark.parametrize('login_transform', [
    lambda n: n,
    partial(add_suffix, '@u.washington.edu'),
    partial(add_suffix, '@washington.edu'),
    partial(add_suffix, '@uw.edu'),
    crazy_casing,
])
def test_new_session_std_sign_on(utils, browser, sp_url, sp_domain, new_tab, secrets, netid, login_transform):
    login = login_transform(netid)
    password = secrets.test_accounts.password
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        browser.get(f'{sp_url(sp)}/shibprod')
        browser.send_inputs(login, password)
        browser.click(Locators.submit_button)
        browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')

    sp = ServiceProviderInstance.diafine12
    with utils.using_test_sp(sp):
        new_tab()
        browser.get(f'{sp_url(sp)}/shibprod')
        browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')

    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        new_tab()
        browser.get(f'{sp_url(sp)}/shibprodforce')
        browser.send_inputs(netid, password)
        browser.click(Locators.submit_button)
        browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        browser.click(Locators.logout_button)
        browser.wait_for_tag('span', 'your uw netid sign-in session has ended.')


# PWD 5
def test_idp_initiated_sign_on(utils, browser, sp_url, sp_domain, secrets, netid):
    sp = ServiceProviderInstance.diafine6
    password = secrets.test_accounts.password
    url = ("https://idp.u.washington.edu/idp/profile/SAML2/Unsolicited/SSO?providerId="
           f"{sp_url(sp)}/shibboleth&shire={sp_url(sp)}/Shibboleth.sso/SAML2/POST")
    with utils.using_test_sp(sp):
        browser.get(url)
        browser.send_inputs(netid, password)
        browser.click(Locators.submit_button)
        browser.wait_for_tag('h1', 'diafine6 idp testing platform')


# PWD 9, 12, 13
@pytest.mark.parametrize('login_transform, password_transform, expected_error_message', [
    # Adds an unsupported suffix to the user's netid
    (partial(add_suffix, '@google.com'), lambda p: p, 'please sign in with your uw netid'),
    # Transforms the user's netid to become one that doesn't exist
    (partial(add_suffix, 'zzz'), lambda p: p, 'your sign-in failed'),
    # Reverses the user's password, so that it is incorrect
    (lambda n: n, lambda p: p[::-1], 'your sign-in failed'),
])
def test_password_sign_on_fails(
        utils: WebTestUtils,
        browser: Chrome,
        sp_url: Callable[[ServiceProviderInstance], str],
        secrets: TestSecrets,
        netid: str,
        login_transform: Callable[[str], str],
        password_transform: Callable[[str], str],
        expected_error_message: str):
    """
    :param login_transform: A function that accepts a string, and returns a string.
    :param password_transform:  A function that accepts a string, and returns a string.
    """
    login = login_transform(netid)
    sp = ServiceProviderInstance.diafine6
    password = password_transform(secrets.test_accounts.password)

    with utils.using_test_sp(sp):
        browser.get(f'{sp_url(sp)}/shibprod')
        browser.send_inputs(login, password)
        browser.click(Locators.submit_button)
        browser.wait_for_tag('p', expected_error_message)


# PWD 11
def test_query_param_forwarding(utils: WebTestUtils, browser: Chrome, sp_url: Callable[[ServiceProviderInstance], str],
                                secrets: TestSecrets, netid: str):
    sp = ServiceProviderInstance.diafine6
    password = secrets.test_accounts.password

    with utils.using_test_sp(sp):

        browser.get(f'{sp_url(sp)}/shibprod/q-param-test.aspx?fname=Joe&lname=Smith&age=30')
        browser.send_inputs(netid, password)
        browser.click(Locators.submit_button)
        browser.wait_for_tag('h1', 'query parameters')
        paragraphs = browser.find_elements_by_tag_name('p')
        assert 'this page should display all parameters from the query string' in paragraphs[0].text
        for snippet in ('fname = Joe', 'lname = Smith', 'age = 30'):
            assert snippet in paragraphs[1].text
