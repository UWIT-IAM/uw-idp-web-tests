import pytest

from tests.access_control import AccessControlTestBase
from tests.models import ServiceProviderInstance


class TestCond2faGroupMember(AccessControlTestBase):
    @pytest.fixture(autouse=True)
    def initialize(self, netid3):
        self.netid = netid3

    def test_a(self):
        """
        Prompted for pwd only on diafine8
        """
        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

    def test_b(self):
        """
        No prompts on diafine8.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_c(self):
        """
        c. Prompted for pwd only on diafine8.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='force'))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

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
        e. Prompted for pwd then 2FA on diafine8.
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
        f. Prompted for pwd then 2FA on diafine8 (no 500 error).
        """
        sp = ServiceProviderInstance.diafine8
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)
