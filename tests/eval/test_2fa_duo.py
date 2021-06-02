"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

2FA-1 thru 2FA-11. 2FA-8b and 2FA-10 are not yet automate-able.
"""

import pytest

from webdriver_recorder.browser import Chrome

from tests.helpers import CTRL_KEY, Locators, WebTestUtils
from tests.models import ServiceProviderInstance, AccountNetid, TestSecrets

from selenium import webdriver


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


def test_new_session_no_duo(utils, sp_url, sp_domain, secrets, netid):
    """
    2FA-1 New session, 2FA sign-in, user doesn't have a Duo account or a TAWS CRN.
    """
    # diafine6, sptest01
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibevalmfa')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'The application you requested requires two-factor authentication (2FA)')
        fresh_browser.close()


class TestNew2FASessionAndExisting2FASession:
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

    def test_2fa_signin(self, secrets, netid3):
        """
        2FA-2 New session, 2FA sign-in
        """

        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(f'{self.sp_url(sp)}/shibevalmfa')
            password = secrets.test_accounts.password
            self.browser.send_inputs(netid3, password)
            self.browser.click(Locators.submit_button)
            self.browser.wait_for_tag('p', 'Use your 2FA device.')
            self.browser.switch_to.frame(self.browser.find_element_by_id('duo_iframe'))
            self.browser.execute_script("document.getElementById('passcode').click()")
            passcode = secrets.test_accounts.duo_code
            self.browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]", passcode)
            self.browser.snap()
            self.browser.execute_script("document.getElementById('passcode').click()")
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_2fa_existing_session(self):
        """
        2FA-3 SSO to new 2FA app with an existing 2FA session
        """
        # diafine12 sptest03
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            self.new_tab()
            self.browser.get(f'{self.sp_url(sp)}/shibevalmfa')
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')


class TestNew2FASessionAndForcedReAuth:
    """
    The two tests are grouped here only because they need to share the same browser instance.
    """
    @pytest.fixture(autouse=True)
    def initialize(self, class_browser, utils, sp_url, sp_domain, new_tab, secrets, netid3):
        self.browser = class_browser
        self.utils = utils
        self.sp_url = sp_url
        self.sp_domain = sp_domain
        self.new_tab = new_tab
        self.netid3 = netid3
        self.password = secrets.test_accounts.password
        self.passcode = secrets.test_accounts.duo_code

    def test_new_session_2fa_invalid_token_retry(self, secrets):
        """
        2FA-4 New session, 2FA sign-in with invalid token and retry
        """
        # provide an invalid token number.
        # provide the correct token number.
        sp = ServiceProviderInstance.diafine6
        self.browser.get(f'{self.sp_url(sp)}/shibevalmfa')
        self.browser.send_inputs(self.netid3, self.password)
        self.browser.click(Locators.submit_button)
        self.browser.wait_for_tag('p', 'Use your 2FA device.')
        self.browser.implicitly_wait(10)
        self.browser.switch_to.frame(self.browser.find_element_by_id('duo_iframe'))
        self.browser.execute_script("document.getElementById('passcode').click()")
        passcode = '0thisisbad0'
        self.browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]", passcode)
        self.browser.snap()
        self.browser.execute_script("document.getElementById('passcode').click()")
        self.browser.wait_for_tag('span', 'Incorrect passcode. Enter a passcode from Duo Mobile.')
        self.browser.execute_script("document.getElementById('passcode').click()")
        self.browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]", self.passcode)
        self.browser.snap()
        self.browser.execute_script("document.getElementById('passcode').click()")
        self.browser.switch_to.default_content()
        self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_forced_reauth_2fa(self):
        """2 FA-5 SSO to new forced reauth 2FA SP with an existing 2FA session"""
        # diafine12, sptest03
        sp = ServiceProviderInstance.diafine12
        self.browser.get(f'{self.sp_url(sp)}/shibevalmfaforce')
        self.browser.send_inputs(self.netid3, self.password)
        self.browser.click(Locators.submit_button)
        self.browser.wait_for_tag('p', 'Use your 2FA device.')
        self.browser.implicitly_wait(10)
        self.browser.switch_to.frame(self.browser.find_element_by_id('duo_iframe'))
        self.browser.execute_script("document.getElementById('passcode').click()")
        self.browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]",
                                    self.passcode)
        self.browser.snap()
        self.browser.execute_script("document.getElementById('passcode').click()")
        self.browser.switch_to.default_content()
        self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')


def test_2fa_user_opt_in(utils, sp_url, sp_domain, secrets, netid4):
    """2FA-6 User opt-in"""
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibeval')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid4, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Use your 2FA device.')
        fresh_browser.switch_to.frame(fresh_browser.find_element_by_id('duo_iframe'))
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        passcode = secrets.test_accounts.duo_code
        fresh_browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]", passcode)
        fresh_browser.snap()
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')


def test_exception_to_user_opt_in(utils, sp_url, sp_domain, secrets, netid5):
    """
    2 FA-7 Exception to user opt-in (opt-out). Opt-out overrides opt-in
    """
    # diafine6, sptest05
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibeval')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid5, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        fresh_browser.close()


def test_2fa_session_using_crn(utils, sp_url, sp_domain, secrets, netid2):
    """
    2FA-8 part a. 2FA session using Single CRN. Part b (2FA session using Multiple CRNs) is not ready for automation.
    To make the automation possible, another test account that has two crns needs to be created.
    """
    # diafine6, sptest02
    # For primary authn, use sptest02 (no 2FA account but with a CRN list of sptest03).
    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibevalmfa')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid2, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Use your 2FA device.')
        fresh_browser.wait_for_tag('p', "Using your 'sptest03' Duo identity.")

        fresh_browser.switch_to.frame(fresh_browser.find_element_by_id('duo_iframe'))
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        passcode = secrets.test_accounts.duo_code
        fresh_browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]", passcode)
        fresh_browser.snap()
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        fresh_browser.close()


        # 2FA-8 part b.
        # Multiple CRNs: IdP displays a CRN chooser and then uses the CRN that was selected.
        # IdP should display a CRN chooser and then uses the CRN that was selected.


def test_remember_me_cookie(utils, sp_url, sp_domain, secrets, netid3, new_tab):
    """
    2FA-9 Remember me cookie
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 1})
    fresh_browser = Chrome(options=chrome_options)

    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibevalmfa')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid3, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Use your 2FA device.')
        fresh_browser.find_element_by_name('rememberme').click()
        fresh_browser.switch_to.frame(fresh_browser.find_element_by_id('duo_iframe'))
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        passcode = secrets.test_accounts.duo_code
        fresh_browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]", passcode)
        fresh_browser.snap()
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        # go to an idp site to retrieve the rememberme cookie
        fresh_browser.get('https://idp-eval.u.washington.edu/idp')
        fresh_browser.wait_for_tag('h1', 'not found')

        # look for these cookies:
        # shib_idp_session, shib_idp_session_ss, and uw-rememberme-sptest03
        cookie_list = fresh_browser.get_cookies()
        wanted_cookie_names = ['shib_idp_session', 'shib_idp_session_ss', 'uw-rememberme-sptest03']

        found_cookies = {}
        for cookie in cookie_list:
            if cookie['name'] in wanted_cookie_names:
                found_cookies[cookie['name']] = 1

        assert(len(found_cookies) == 3)

        # b Sign out of the IdP to clear the 2FA session
        fresh_browser.get('https://diafine6.sandbox.iam.s.uw.edu/Shibboleth.sso/Logout?return=https://idp-eval.u'
                          '.washington.edu/idp/profile/Logout')
        # After signing out of the IdP, the rememberme cookie should remain in the browser,
        # but shib_idp_session* cookies should be gone.
        fresh_browser.wait_for_tag('span', 'Your UW NetID sign-in session has ended.')

        sign_out_cookie_list = fresh_browser.get_cookies()
        found_rememberme = False
        for cookie in sign_out_cookie_list:
            if cookie['name'] == 'uw-rememberme-sptest03':
                found_rememberme = True
            else:
                assert cookie['name'] not in wanted_cookie_names
        assert found_rememberme is True

        # c Navigate to the Eval "Token authn" link on (https://diafine12.sandbox.iam.s.uw.edu/shibevalmfa)
        sp = ServiceProviderInstance.diafine12
        with utils.using_test_sp(sp):
            fresh_browser.get(f'{sp_url(sp)}/shibevalmfa')
            password = secrets.test_accounts.password
            fresh_browser.send_inputs(netid3, password)
            fresh_browser.click(Locators.submit_button)
            fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        fresh_browser.close()


def test_forget_me_admin():
    """
    2FA-10 Forget me (admin) per Michael, this test is not yet ready to be automated.
    """


def test_forget_me_self_service(utils, sp_url, sp_domain, secrets, netid3, new_tab):
    """
    2FA-11 Forget me (self-service)
    """
    # diafine6, sptest03

    fresh_browser = Chrome()
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibevalmfa')
        password = secrets.test_accounts.password
        fresh_browser.send_inputs(netid3, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('p', 'Use your 2FA device.')
        fresh_browser.find_element_by_name('rememberme').click()
        fresh_browser.switch_to.frame(fresh_browser.find_element_by_id('duo_iframe'))
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        passcode = secrets.test_accounts.duo_code
        fresh_browser.execute_script("document.getElementsByClassName('passcode-input')[0].value=arguments[0]",
                                     passcode)
        fresh_browser.snap()
        fresh_browser.execute_script("document.getElementById('passcode').click()")
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        # go to an idp site to retrieve the rememberme cookie
        fresh_browser.get('https://idp-eval.u.washington.edu/idp')
        fresh_browser.wait_for_tag('h1', 'not found')
        # look for this cookie:
        # uw-rememberme-sptest03
        cookie_list = fresh_browser.get_cookies()
        wanted_cookie_name = 'uw-rememberme-sptest03'

        found_cookie = False
        cookie_removed = True
        for cookie in cookie_list:
            # print('cookie.values ', cookie.values())
            if wanted_cookie_name in cookie.values():
                found_cookie = True

        # b. Navigate to https://idp.u.washington.edu/forgetme (https://idp-eval.u.washington.edu/forgetme)?
        # IdP responds with "The 2FA "Remember me on this browser" setting has been removed from this browser."
        # The cookie named uw-rememberme-sptest03 should be gone.
        # Close browser.

        if found_cookie:
            fresh_browser.get('https://idp-eval.u.washington.edu/forgetme')
            fresh_browser.wait_for_tag('p', 'setting has been removed from this browser.')
            cookie_list = fresh_browser.get_cookies()
            for cookie in cookie_list:
                if wanted_cookie_name in cookie.values():
                    cookie_removed = False

        assert (found_cookie is True and cookie_removed is True)







