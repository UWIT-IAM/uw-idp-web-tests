import pytest

from tests.access_control import AccessControlTestBase
from tests.models import ServiceProviderInstance


class TestCond2faGroupMember(AccessControlTestBase):
    @pytest.fixture(autouse=True)
    def initialize(self, netid6):
        """
        AC-2.1 Conditional 2FA, tester is group member.
        """
        self.netid = netid6

    def test_a(self):
        """
        a. Prompted for pwd then 2FA on diafine8.
        """
        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_b(self):
        """
        b. Prompted for 2FA only on diafine8.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_c(self):
        """
        c. Prompted for pwd then 2FA on diafine8.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='force'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_d(self):
        """
        d. No prompts on diafine8.
        """

        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_e(self):
        """
        Prompted for pwd then 2FA on diafine8.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfaforce'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_f(self):
        """
        Prompted for pwd then 2FA on diafine8 (no 500 error).
        """
        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)
