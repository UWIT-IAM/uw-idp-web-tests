import pytest
from webdriver_recorder.browser import Chrome
from tests.models import ServiceProviderInstance


class TestCond2faNonMemberBoth:
    @pytest.fixture(autouse=True)
    def initialize(self, utils, secrets, sp_url, test_env, sp_domain, two_fa_submit_form, login_submit_form, netid3):
        """
        AC-5.2	Conditional 2FA + conditional access, tester is not member of either group.
        diafine11, sptest03
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
        a. Prompted for pwd, then access denied on diafine11. Access error URL returned.
        Close browser.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_b(self):
        """
        b. Access denied on diafine11. Access error URL returned.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_c(self):
        """
        c. Start pwd SSO session at https://diafine6.sandbox.iam.s.uw.edu/shibeval.
        Use SSO to access https://diafine11.sandbox.iam.s.uw.edu/shibevalforce.
        c. Prompted for pwd, then access denied on diafine11. Access error URL returned.
        Close browser.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}force')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_d(self):
        """
        d. Access denied on diafine11. Access error URL returned.
        Close browser.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_e(self):
        """
        e. Prompted for pwd, then 2FA, then access denied on diafine11.
         Access error URL returned.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfaforce')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

    def test_f(self):
        """
        f. Prompted for pwd then 2FA, then access denied on diafine11 (no 500 error).
        Access error URL returned.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('p', 'You are not authorized to access the application:')
            fresh_browser.close()

