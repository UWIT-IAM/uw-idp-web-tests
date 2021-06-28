import pytest
from webdriver_recorder.browser import Chrome
from tests.models import ServiceProviderInstance


class TestCondAccessMember:
    @pytest.fixture(autouse=True)
    def initialize(self, utils, secrets, sp_url, test_env, sp_domain, two_fa_submit_form, login_submit_form, netid7):
        """
        AC-4.1	Auto 2FA + conditional access, tester is group member.
        diafine10, sptest07
        """
        self.utils = utils
        self.sp_url = sp_url
        self.sp_domain = sp_domain
        self.password = secrets.test_accounts.password
        self.passcode = secrets.test_accounts.duo_code
        self.test_env = test_env
        self.two_fa_submit_form = two_fa_submit_form
        self.login_submit_form = login_submit_form
        self.netid = netid7

    def test_a(self):
        """
        a. Prompted for pwd then 2FA on diafine10.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            fresh_browser.close()

    def test_b(self):
        """
        b. Prompted for 2FA only on diafine10.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            fresh_browser.close()

    def test_c(self):
        """
        c. Prompted for pwd then 2FA on diafine10.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}force')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            fresh_browser.close()

    def test_d(self):
        """
        d. No prompts on diafine10.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            fresh_browser.close()

    def test_e(self):
        """
        e. Prompted for pwd then 2FA on diafine10.
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfaforce')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            fresh_browser.close()

    def test_f(self):
        """
        f. Prompted for pwd then 2FA on diafine10 (no 500 error).
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, self.netid, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            fresh_browser.close()