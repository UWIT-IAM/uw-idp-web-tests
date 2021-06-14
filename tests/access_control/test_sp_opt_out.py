import pytest
from webdriver_recorder.browser import Chrome
from tests.models import ServiceProviderInstance


class TestSpOptOut:
    @pytest.fixture(autouse=True)
    def initialize(self, utils, secrets, sp_url, test_env, sp_domain, two_fa_submit_form, login_submit_form):
        """
        AC-6 SP opt-out	diafine12, sptest03, sptest04
        """
        self.utils = utils
        self.sp_url = sp_url
        self.sp_domain = sp_domain
        self.password = secrets.test_accounts.password
        self.passcode = secrets.test_accounts.duo_code
        self.test_env = test_env
        self.two_fa_submit_form = two_fa_submit_form
        self.login_submit_form = login_submit_form

    def test_a(self, netid3):
        """
        a. Prompted for pwd (SP opt-out trumps auto-2FA).
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, netid3, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
            fresh_browser.close()

    def test_b(self, netid4):
        """
        b. Sign in sptest04 using the Eval "Password authn" link (https://diafine12.sandbox.iam.s.uw.edu/shibeval).
        b. Prompted for pwd (SP opt-out trumps user opt-in).
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}')
            self.login_submit_form(fresh_browser, netid4, self.password)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_c(self, netid3):
        """
        c. Sign in sptest03 using the Eval "Token authn" link (https://diafine12.sandbox.iam.s.uw.edu/shibevalmfa).
        c. Prompted for pwd, then 2FA (requested MFA authnContextClassRef trumps SP opt-out).
        """
        fresh_browser = Chrome()
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            fresh_browser.get(f'{self.sp_url(sp)}/shib{self.test_env}mfa')
            self.login_submit_form(fresh_browser, netid3, self.password)
            self.two_fa_submit_form(fresh_browser)
            fresh_browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
