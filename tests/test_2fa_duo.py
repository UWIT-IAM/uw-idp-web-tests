"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

2FA-1 thru 2FA-11. 2FA-8b and 2FA-10 are not yet automatable.
"""
from webdriver_recorder.browser import Chrome
from tests.helpers import Locators
from tests.models import ServiceProviderInstance
import pytest



def add_suffix(suffix: str, netid: str) -> str:
    return f'{netid}{suffix}'


def test_new_session_no_duo(utils, sp_url, sp_domain, secrets, netid, test_env, fresh_browser, sp_shib_url):
    """
    2FA-1 New session, 2FA sign-in, user doesn't have a Duo account or a TAWS CRN.
    """
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(sp_shib_url(sp, append='mfa'))
        password = secrets.test_accounts.password.get_secret_value()
        fresh_browser.send_inputs(netid, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'The application you requested requires two-factor authentication (2FA)')


@pytest.mark.usefixtures('fresh_class_browser')
class TestNew2FASessionAndExisting2FASession:
    browser: Chrome

    """
    The two tests are grouped here only because they need to share the same browser instance.
    """

    @pytest.fixture(autouse=True)
    def initialize(self, utils, sp_domain, sp_shib_url):
        self.utils = utils
        self.sp_domain = sp_domain
        self.sp_shib_url = sp_shib_url

    def test_2fa_signin(self, secrets, netid3, enter_duo_passcode, log_in_netid):
        """
        2FA-2 New session, 2FA sign-in
        """

        password = secrets.test_accounts.password.get_secret_value()

        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            log_in_netid(self.browser, netid3, assert_success=False)
            enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_2fa_existing_session(self):
        """
        2FA-3 SSO to new 2FA app with an existing 2FA session
        """
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            with self.browser.tab_context():
                self.browser.get(self.sp_shib_url(sp, append='mfa'))
                self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')


@pytest.mark.usefixtures('fresh_class_browser')
class TestNew2FASessionAndForcedReAuth:
    """
    The two tests are grouped here only because they need to share the same browser instance.
    """
    browser: Chrome

    @pytest.fixture(autouse=True)
    def initialize(self, utils, sp_shib_url, sp_domain, secrets, netid3, test_env, enter_duo_passcode):
        self.utils = utils
        self.sp_shib_url = sp_shib_url
        self.sp_domain = sp_domain
        self.netid = netid3
        self.password = secrets.test_accounts.password.get_secret_value()
        self.test_env = test_env
        self.enter_duo_passcode = enter_duo_passcode

    def test_new_session_2fa_invalid_token_retry(self, log_in_netid):
        """
        2FA-4 New session, 2FA sign-in with invalid token and retry
        """
        passcode = '0thisisbad0'
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser,
                                    passcode=passcode,
                                    assert_failure=True)
            self.enter_duo_passcode(self.browser,
                                    select_iframe=False,
                                    match_service_provider=sp,
                                    assert_success=True)

    def test_forced_reauth_2fa(self):
        """2 FA-5 SSO to new forced reauth 2FA SP with an existing 2FA session"""
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfaforce'))
            self.browser.send_inputs(self.netid, self.password)
            self.browser.click(Locators.submit_button)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)


def test_2fa_user_opt_in(utils, sp_shib_url, sp_domain, secrets, netid4, test_env, fresh_browser, enter_duo_passcode):
    """2FA-6 User opt-in"""
    sp = ServiceProviderInstance.diafine6
    password = secrets.test_accounts.password.get_secret_value()
    with utils.using_test_sp(sp):
        fresh_browser.get(sp_shib_url(sp))
        fresh_browser.send_inputs(netid4, password)
        fresh_browser.click(Locators.submit_button)
        enter_duo_passcode(fresh_browser, match_service_provider=sp)


def test_exception_to_user_opt_in(utils, sp_shib_url, sp_domain, secrets, netid5, test_env, fresh_browser):
    """
    2 FA-7 Exception to user opt-in (opt-out). Opt-out overrides opt-in
    """
    sp = ServiceProviderInstance.diafine6
    password = secrets.test_accounts.password.get_secret_value()
    with utils.using_test_sp(sp):
        fresh_browser.get(sp_shib_url(sp))
        fresh_browser.send_inputs(netid5, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')


class Test2FASessionCRNs:
    """
    The two tests are grouped here as they excersise CRNs.
    """
    browser: Chrome

    @pytest.fixture(autouse=True)
    def initialize(self, utils, sp_shib_url, sp_domain, secrets, test_env, fresh_browser):
        self.browser = fresh_browser
        self.utils = utils
        self.sp_domain = sp_domain
        self.password = secrets.test_accounts.password.get_secret_value()
        self.test_env = test_env
        self.sp = ServiceProviderInstance.diafine6
        self.shib_mfa_url = sp_shib_url(self.sp, append='mfa')

    def test_2fa_session_single_crn(self, netid2, enter_duo_passcode):
        """
        2FA-8 part a. 2FA session using an acct with a Single CRN.
        """
        # For primary authn, use sptest02 (no 2FA account but with a CRN list of sptest03).
        with self.utils.using_test_sp(self.sp):
            self.browser.get(self.shib_mfa_url)
            self.browser.send_inputs(netid2, self.password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('p', "Using your 'sptest03' Duo identity.")
            enter_duo_passcode(self.browser, match_service_provider=self.sp)

    def test_2fa_session_multiple_crn(self, netid10, enter_duo_passcode):
        """
        2FA-8 part b. 2FA session using an acct with multiple CRNs.
        """
        # b. For primary authn, use sptest10 (no 2FA account but with a CRN list of sptest03, sptest07).
        with self.utils.using_test_sp(self.sp):
            self.browser.get(self.shib_mfa_url)
            self.browser.send_inputs(netid10, self.password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('div', 'Select a UW NetID for 2nd factor authentication.')
            self.browser.find_element_by_xpath("//input[@value='sptest07']").click()
            self.browser.snap()
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('p', "Using your 'sptest07' Duo identity.")
            enter_duo_passcode(self.browser, match_service_provider=self.sp)


def test_remember_me_cookie(
        utils, sp_shib_url, sp_url, log_in_netid,
        sp_domain, secrets, netid3, test_env, fresh_browser, enter_duo_passcode):
    """
    2FA-9 Remember me cookie
    """
    fresh_browser
    password = secrets.test_accounts.password.get_secret_value()

    idp_env = '-eval' if test_env == 'eval' else ''
    idp_url = f'https://idp{idp_env}.u.washington.edu/idp'

    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(sp_shib_url(sp, append='mfa'))
        fresh_browser.send_inputs(netid3, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Use your 2FA device.')
        fresh_browser.find_element_by_name('rememberme').click()
        enter_duo_passcode(fresh_browser, match_service_provider=sp)
        # go to an idp site to retrieve the rememberme cookie
        fresh_browser.get(idp_url)
        fresh_browser.wait_for_tag('h1', 'not found')

        # look for these cookies:
        # shib_idp_session, shib_idp_session_ss, and uw-rememberme-sptest03

        cookie_names = {cookie['name'] for cookie in fresh_browser.get_cookies()}
        assert 'shib_idp_session' in cookie_names
        assert 'shib_idp_session_ss' in cookie_names
        assert 'uw-rememberme-sptest03' in cookie_names

        fresh_browser.get(f'{sp_url(sp)}/Shibboleth.sso/Logout?return={idp_url}/profile/Logout')
        # After signing out of the IdP, the rememberme cookie should remain in the browser,
        # but shib_idp_session* cookies should be gone.
        fresh_browser.wait_for_tag('span', 'Your UW NetID sign-in session has ended.')

        cookie_names = {cookie['name'] for cookie in fresh_browser.get_cookies()}
        assert 'shib_idp_session' not in cookie_names
        assert 'shib_idp_session_ss' not in cookie_names
        assert 'uw-rememberme-sptest03' in cookie_names

    sp = ServiceProviderInstance.diafine12
    with utils.using_test_sp(sp):
        fresh_browser.get(sp_shib_url(sp, append='mfa'))
        log_in_netid(fresh_browser, netid3, match_service_provider=sp)


def test_forget_me_self_service(utils, sp_url, sp_domain, secrets, netid3, test_env, enter_duo_passcode,
                                fresh_browser, sp_shib_url):
    """
    2FA-11 Forget me (self-service)
    """
    idp_env = ''
    if test_env == "eval":
        idp_env = "-eval"

    browser = fresh_browser
    cookie_name = 'uw-rememberme-sptest03'
    password = secrets.test_accounts.password.get_secret_value()

    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        browser.get(sp_shib_url(sp, append='mfa'))
        browser.send_inputs(netid3, password)
        browser.click(Locators.submit_button)
        browser.wait_for_tag('p', 'Use your 2FA device.')
        browser.find_element_by_name('rememberme').click()
        enter_duo_passcode(browser, match_service_provider=sp)
        # go to an idp site to retrieve the rememberme cookie
        browser.get(f'https://idp{idp_env}.u.washington.edu/idp')
        browser.wait_for_tag('h1', 'not found')

        cookies_names = list(c['name'] for c in browser.get_cookies())
        assert cookie_name in cookies_names

        browser.get(f'https://idp{idp_env}.u.washington.edu/forgetme')
        browser.wait_for_tag('p', 'setting has been removed from this browser.')
        cookies_names = list(c['name'] for c in browser.get_cookies())
        assert cookie_name not in cookies_names
