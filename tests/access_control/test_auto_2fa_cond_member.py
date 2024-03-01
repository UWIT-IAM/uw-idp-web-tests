import pytest
from webdriver_recorder.browser import Chrome

from tests.access_control import AccessControlTestBase
from tests.models import ServiceProviderInstance


class TestCondAccessMember(AccessControlTestBase):
    """
    Tests that diafine10 forces 2fa in a variety of cases
    """
    @pytest.fixture(autouse=True)
    def initialize(self, netid7):
        self.netid = netid7

    def test_a(self):
        """
        a. Prompted for pwd then 2FA on diafine10.
        """
        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_b(self):
        """
        b. Prompted for 2FA only on diafine10.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_c(self):
        """
        c. Prompted for pwd then 2FA on diafine10 even after logging in to diafine6.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='force'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp, is_this_your_device_screen=False)

    def test_d(self):
        """
        d. No prompts on diafine10.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_e(self):
        """
        e. Prompted for pwd then 2FA on diafine10 even after diafine6 requested 2fa.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfaforce'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp, is_this_your_device_screen=False)

    def test_f(self):
        """
        f. Prompted for pwd then 2FA on diafine10 (no 500 error).
        """
        sp = ServiceProviderInstance.diafine10
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)
