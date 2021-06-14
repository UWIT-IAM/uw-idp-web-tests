import pytest
from webdriver_recorder.browser import Chrome
from tests.models import ServiceProviderInstance


class TestCondAccessNonMember:
    @pytest.fixture(autouse=True)
    def initialize(self, utils, secrets, sp_url, test_env, sp_domain, two_fa_submit_form, login_submit_form, netid3):
        """
        AC-3.2	Conditional access, tester is not group member.
        diafine9, sptest03
        """
        self.utils = utils
        self.sp_url = sp_url
        self.sp_domain = sp_domain
        self.password = secrets.test_accounts.password
        self.passcode = secrets.test_accounts.duo_code
        self.test_env = test_env
        self.two_fa_submit_form = two_fa_submit_form
        self.login_submit_form = login_submit_form
        self.netid = netid3

    def test_a(self):
        """
        Access error URL returned on diafine9.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.set_window_size(500, 1000)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_b(self):
        """
        Access denied on diafine9. Access error URL returned.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            fresh_browser.set_window_size(500, 1000)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_c(self):
        """
        c. Prompted for pwd, then access denied on diafine9. Access error URL returned.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}force')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.set_window_size(500, 1000)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_d(self):
        """
        d. Start 2FA session at https://diafine6.sandbox.iam.s.uw.edu/shibevalmfa.
        Use SSO to access https://diafine9.sandbox.iam.s.uw.edu/shibevalmfa.
        Close browser.
        d. Access denied on diafine9. Access error URL returned.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            fresh_browser.set_window_size(600, 1000)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_e(self):
        """
        e. Start 2FA session at https://diafine6.sandbox.iam.s.uw.edu/shibevalmfa.
        Use SSO to access https://diafine9.sandbox.iam.s.uw.edu/shibevalmfaforce.
        Close browser.
        e. Prompted for pwd, then 2FA, then access denied on diafine9. Access error URL returned.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfaforce')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()
