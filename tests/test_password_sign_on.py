"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

PWD-1 thru PWD-9.
PWD-10	Blacklisted cookie (disuser case) is not covered here. This comment can be removed when AUTH-1474 is resolved.
"""


from functools import partial

import pytest
from webdriver_recorder.browser import Chrome

from tests.helpers import Locators
from tests.models import ServiceProviderInstance


def add_suffix(suffix: str, netid: str) -> str:
    return f'{netid}{suffix}'


def lower_upper_casing(netid: str) -> str:
    def inner():
        letters = list(netid)
        for i, letter in enumerate(letters):
            if i % 2 == 0:
                letters[i] = letter.upper()
        return ''.join(letters)
    return inner()


@pytest.mark.usefixtures('fresh_class_browser')
class TestNewSessionAndExistingSSOSession:
    """
    The two tests are grouped here only because they need to share the same browser instance.
    """
    @pytest.fixture(autouse=True)
    def initialize(self, utils, sp_shib_url, sp_domain, test_env):
        self.utils = utils
        self.sp_domain = sp_domain
        self.test_env = test_env
        self.sp_shib_url = sp_shib_url

    def test_new_session_standard(self, secrets, netid):
        """
        PWD-1. New standard session, password sign-in
        """
        password = secrets.test_accounts.password.get_secret_value()
        sp = ServiceProviderInstance.diafine8

        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.browser.send_inputs(netid, password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_existing_sso_session(self):
        """
        PWD-2. Use existing pwd SSO session for sign-in
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            with self.browser.autocapture_off():
                self.browser.get(self.sp_shib_url(sp))
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_logout(self):
        """
        PWD-3. Log out.
        """
        self.browser.click_tag('a', 'Return to the main menu')
        with self.browser.autocapture_off():
            self.browser.wait_for_tag('h1', 'Diafine6 IdP Testing Platform')
        self.browser.click_tag('a', 'Logout')
        self.browser.wait_for_tag('span', 'Your UW NetID sign-in session has ended')


@pytest.mark.usefixtures('fresh_class_browser')
class TestCredentialsAndForcedReauth:
    """
    The two tests are grouped here only because they need to share the same browser instance.
    """
    browser: Chrome

    @pytest.fixture(autouse=True)
    def initialize(self, utils, secrets, netid, test_env, sp_shib_url):
        self.utils = utils
        self.netid = netid
        self.sp_shib_url = sp_shib_url
        self.password = secrets.test_accounts.password.get_secret_value()
        self.test_env = test_env

    def test_new_session_standard_bad_creds(self):
        """
        PWD-4. New session, password sign-in, bad creds.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            bad_netid = 'non-existent-0123456789'
            self.browser.send_inputs(bad_netid, self.password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('p', 'Your sign-in failed.')
            element = self.browser.find_element_by_id('weblogin_netid')
            element.click()
            element.clear()
            bad_password = '1'
            self.browser.send_inputs(self.netid, bad_password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('p', 'Your sign-in failed.')

    def test_existing_sso_for_sign_in_with_forced_reauth(self, sp_domain, log_in_netid):
        """
        PWD-5 Use existing pwd SSO session for sign-in, combined with forced reauth
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            with self.browser.tab_context():
                self.browser.get(self.sp_shib_url(sp, append='force'))
                log_in_netid(self.browser, self.netid, match_service_provider=sp)


def test_idp_initiated_sign_in(netid, utils, sp_url, secrets, sp_domain, test_env, fresh_browser):
    """
    PWD-6 IdP-initiated sign-in
    """
    fresh_browser.set_window_size(1024, 768)
    sp = ServiceProviderInstance.diafine6
    idpenv = ''
    if test_env == "eval":
        idpenv = "-eval"
    with utils.using_test_sp(sp):
        fresh_browser.get(f'https://idp{idpenv}.u.washington.edu/idp/profile/SAML2/Unsolicited/SSO?providerId=https'
                          '://diafine6.sandbox.iam.s.uw.edu/shibboleth&shire=https://diafine6.sandbox.iam.s.uw.edu'
                          '/Shibboleth.sso/SAML2/POST')
        password = secrets.test_accounts.password.get_secret_value()
        fresh_browser.send_inputs(netid, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h1', 'Diafine6 IdP Testing Platform')
        fresh_browser.get(f'{sp_url(sp)}/Shibboleth.sso/Session')
        fresh_browser.wait_for_tag('u', 'Miscellaneous')
        with fresh_browser.autocapture_off():
            fresh_browser.wait_for_tag('strong', 'Session Expiration (barring inactivity):')


@pytest.mark.parametrize('login_transform', [
    partial(add_suffix, '@u.washington.edu'),
    partial(add_suffix, '@washington.edu'),
    partial(add_suffix, '@uw.edu'),
    partial(add_suffix, '@google.com')
])
def test_new_session_sign_on_domain_credential(
        browser, netid, utils, sp_shib_url, log_in_netid,
        secrets, sp_domain, login_transform, test_env, fresh_browser):
    """
    PWD-7 New session, sign on with @domain credential format
    """
    login = login_transform(netid)
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(sp_shib_url(sp))

        assert_login_success = 'google' not in login
        log_in_netid(fresh_browser, login, assert_success=assert_login_success)
        if not assert_login_success:
            fresh_browser.wait_for_tag('p', 'Please sign in with your UW NetID')


@pytest.mark.usefixtures('fresh_class_browser')
class TestNetIDCaseInsensitivityAndURLQueryParams:
    """
    The two tests are grouped here only because they need to share the same browser instance.
    """
    @pytest.fixture(autouse=True)
    def initialize(self, secrets, utils, test_env, sp_shib_url):
        self.password = secrets.test_accounts.password.get_secret_value()
        self.sp = ServiceProviderInstance.diafine6
        self.utils = utils
        self.sp_shib_url = sp_shib_url
        self.test_env = test_env
        self.lower_upper_casing = lower_upper_casing

    def test_case_insensitivity(self, netid, sp_domain):
        """
        PWD-8 Case insensitivity
        """
        mixed_case_netid = self.lower_upper_casing(netid)
        with self.utils.using_test_sp(self.sp):
            self.browser.get(self.sp_shib_url(self.sp))
            self.browser.send_inputs(mixed_case_netid, self.password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('h2', f'{sp_domain(self.sp)} sign-in success!')

    def test_query_parameters(self,  netid):
        """
        PWD-9 Query parameters
        """
        url = self.sp_shib_url(self.sp)
        url = f'{url}/q-param-test.aspx?fname=Joe&lname=Smith&age=30'
        with self.utils.using_test_sp(self.sp):
            self.browser.snap()
            self.browser.get(url)
            self.browser.wait_for_tag('h1', 'query parameters')
            element = self.browser.find_elements_by_tag_name('p')
            for snippet in ('fname = Joe', 'lname = Smith', 'age = 30'):
                assert (snippet in element[1].text)
