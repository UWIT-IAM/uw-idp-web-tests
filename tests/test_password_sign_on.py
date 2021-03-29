"""
This set of tests is based on the manual tests here
https://wiki.cac.washington.edu/display/SMW/Glen%27s+IdP+practice+Matrix
PWD-1 thru PWD-9.
"""


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


class TestNewSessionAndExistingSSOSession:
    """
    The two tests are grouped here only because they need to share the same browser instance.
    """
    @pytest.fixture(autouse=True)
    def initialize(self, class_browser, utils, sp_url, sp_domain, new_tab):
        self.browser = class_browser
        self.utils = utils
        self.sp_url = sp_url
        self.sp_domain = sp_domain
        self.new_tab = new_tab

    def test_new_session_standard(self, secrets, netid):
        # 1 New session, standard sign-in
        password = secrets.test_accounts.password
        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(f'{self.sp_url(sp)}/shibprod')
            self.browser.send_inputs(netid, password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_existing_sso_session(self):
        # 2 Use existing pwd SSO session for sign-in
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.new_tab()
            with self.browser.autocapture_off():
                self.browser.get(f'{self.sp_url(sp)}/shibprod')
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
        # 3 logout and close browser
            with self.browser.autocapture_off():
                self.browser.click_tag('a', 'Return to the main menu')
            with self.browser.autocapture_off():
                self.browser.wait_for_tag('h1', 'Diafine6 IdP Testing Platform')
            self.browser.click_tag('a', 'Logout')
            self.browser.wait_for_tag('span', 'Your UW NetID sign-in session has ended')


def test_new_session_standard_bad_creds(utils, browser, sp_url, secrets, netid):
    # 4 New session, standard sign-in, bad creds
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibprod')
        password = secrets.test_accounts.password
        badnetid = 'non-existant-0123456789'
        fresh_browser.send_inputs(badnetid, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Your sign-in failed.')
        element = fresh_browser.find_element_by_id('weblogin_netid')
        element.click()
        element.clear()
        badpassword = '1'
        fresh_browser.send_inputs(netid, badpassword)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Your sign-in failed.')
        fresh_browser.close()


def test_existing_sso_for_sign_in_with_forced_reauth(utils, browser, sp_url, secrets, netid, sp_domain, new_tab):
    # 5 Use existing pwd SSO session for sign-in, combined with forced reauth
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibprod')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')

    sp = ServiceProviderInstance.diafine8
    with utils.using_test_sp(sp):
        new_tab()
        fresh_browser.get(f'{sp_url(sp)}/shibprodforce')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        fresh_browser.close()


def test_idp_initiated_sign_in(browser, netid, utils, sp_url, secrets, sp_domain):
    # 6 IdP-initiated sign-in
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get('https://idp.u.washington.edu/idp/profile/SAML2/Unsolicited/SSO?providerId=https://diafine6'
                          '.sandbox.iam.s.uw.edu/shibboleth&shire=https://diafine6.sandbox.iam.s.uw.edu/Shibboleth'
                          '.sso/SAML2/POST')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h1', 'Diafine6 IdP Testing Platform')
        fresh_browser.get('https://diafine6.sandbox.iam.s.uw.edu/Shibboleth.sso/Session')
        fresh_browser.wait_for_tag('u', 'Miscellaneous')
        with fresh_browser.autocapture_off():
            fresh_browser.wait_for_tag('strong', 'Session Expiration (barring inactivity):')
    fresh_browser.close()


@pytest.mark.parametrize('login_transform', [
    partial(add_suffix, '@u.washington.edu'),
    partial(add_suffix, '@washington.edu'),
    partial(add_suffix, '@uw.edu'),
    partial(add_suffix, '@google.com')
])
def test_new_session_sign_on_domain_credential(browser, netid, utils, sp_url, secrets, sp_domain, login_transform):
    # 7 New session, sign on with @domain credential format
    fresh_browser = Chrome()
    login = login_transform(netid)
    password = secrets.test_accounts.password
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibprod')
        fresh_browser.send_inputs(login, password)
        fresh_browser.click(Locators.submit_button)
        if 'google' not in login:
            fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        else:
            element = fresh_browser.wait_for_tag('p', 'Please sign in with your')
            assert ('Please sign in with your UW NetID' in element.text)
    fresh_browser.close()


class TestNetIDCaseInsensitivityAndURLQueryParams:
    """
    The two tests are grouped here only because they need to share the same browser instance.
    """
    @pytest.fixture(autouse=True)
    def initialize(self, class_browser, secrets, utils, sp_url):
        self.browser = class_browser
        self.password = secrets.test_accounts.password
        self.sp = ServiceProviderInstance.diafine6
        self.utils = utils
        self.sp_url = sp_url

    def test_case_insensitivity(self, netid, sp_domain):
        # 8 Case insensitivity
        crazy_netid = crazy_casing(netid)
        with self.utils.using_test_sp(self.sp):
            self.browser.get(f'{self.sp_url(self.sp)}/shibprod')
            self.browser.send_inputs(crazy_netid, self.password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('h2', f'{sp_domain(self.sp)} sign-in success!')

    def test_query_parameters(self,  netid):
        # 9 Query parameters
        with self.utils.using_test_sp(self.sp):
            self.browser.snap()
            self.browser.get(f'{self.sp_url(self.sp)}/shibprod/q-param-test.aspx?fname=Joe&lname=Smith&age=30')
            self.browser.wait_for_tag('h1', 'query parameters')
            element = self.browser.find_elements_by_tag_name('p')
            for snippet in ('fname = Joe', 'lname = Smith', 'age = 30'):
                assert (snippet in element[1].text)
