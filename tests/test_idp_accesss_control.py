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


class TestAuto2fa:
    @pytest.fixture(autouse=True)
    def initialize(self, browser, netid03, utils, sp_url, secrets, sp_domain, new_tab):
        self.browser = browser
        self.netid03 = netid03
        self.utils = utils
        self.sp_url = sp_url
        self.secrets = secrets
        self.sp_domain = sp_domain
        self.new_tab = new_tab

    def test_diafine7_no_pw_sso_auto2fa(self):
        """
        AC-1	Auto 2FA	diafine7, sptest03
        a. Start new pwd session at https://diafine7.sandbox.iam.s.uw.edu/shibprod. Close browser.
        b. Start pwd SSO session at https://diafine6.sandbox.iam.s.uw.edu/shibprod.
            Use SSO to access https://diafine7.sandbox.iam.s.uw.edu/shibprod. Close browser.
        """

        # a
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shibprod')
            password = self.secrets.test_accounts.password
            fresh_browser.send_inputs(self.netid03, password)
            fresh_browser.click(Locators.submit_button)
            fresh_browser.wait_for_tag('p', 'Use your 2fa device')
            fresh_browser.close()

        # b
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shibprod')
            password = self.secrets.test_accounts.password
            fresh_browser.send_inputs(self.netid03, password)
            fresh_browser.click(Locators.submit_button)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            self.new_tab()
            sp = ServiceProviderInstance.diafine7
            fresh_browser.get(f'{self.sp_url(sp)}/shibprod')
            fresh_browser.wait_for_tag('p', 'Use your 2fa device')
            fresh_browser.close()

    def test_diafine7_pwd_2fa(self):
        """
        c.  Start pwd SSO session at https://diafine6.sandbox.iam.s.uw.edu/shibprod.
            Use SSO to access https://diafine7.sandbox.iam.s.uw.edu/shibprodforce.
            Close browser.
            -> Prompted for pwd then 2FA on diafine7.
        """

        # Start pwd SSO session at https://diafine6.sandbox.iam.s.uw.edu/shibprod.
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shibprod')
            password = self.secrets.test_accounts.password
            fresh_browser.send_inputs(self.netid03, password)
            fresh_browser.click(Locators.submit_button)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
        # Use SSO to access https://diafine7.sandbox.iam.s.uw.edu/shibprodforce.
        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shibprodforce')
            password = self.secrets.test_accounts.password
            fresh_browser.send_inputs(self.netid03, password)
            fresh_browser.click(Locators.submit_button)
            fresh_browser.wait_for_tag('p', 'Use your 2fa device')
            fresh_browser.close()

            """
            BLOCKED ON TESTS D,E AND F DUE TO DUO IFRAME
            """
