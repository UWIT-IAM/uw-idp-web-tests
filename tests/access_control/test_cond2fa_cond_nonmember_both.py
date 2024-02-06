import pytest

from tests.access_control import AccessControlTestBase
from tests.models import ServiceProviderInstance


class TestCond2faNonMemberBoth(AccessControlTestBase):
    @pytest.fixture(autouse=True)
    def initialize(self, netid3):
        """
        AC-5.2	Conditional 2FA + conditional access, tester is not member of either group.
        diafine11, sptest03
        """
        self.netid = netid3

    def test_a(self):
        """
        a. Prompted for pwd, then access denied on diafine11. Access error URL returned.
        """
        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.browser.wait_for_tag('p', 'You are not authorized to access the application:')

    def test_b(self):
        """
        b. Access denied on diafine11. Access error URL returned.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.browser.wait_for_tag('p', 'You are not authorized to access the application:')

    def test_c(self):
        """
        c. Prompted for pwd, then access denied on diafine11. Access error URL returned.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid)
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='force'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.browser.wait_for_tag('p', 'You are not authorized to access the application:')

    def test_d(self):
        """
        d. Access denied on diafine11. Access error URL returned.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.browser.wait_for_tag('p', 'You are not authorized to access the application:')

    def test_e(self):
        """
        e. Prompted for pwd, then 2FA, then access denied on diafine11.  Access error URL returned.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfaforce'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, assert_success=False)
            self.browser.switch_to.default_content()
            self.browser.wait_for_tag('p', 'You are not authorized to access the application:')

    def test_f(self):
        """
        f. Prompted for pwd then 2FA, then access denied on diafine11 (no 500 error).  Access error URL returned.
        """
        sp = ServiceProviderInstance.diafine11
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, self.netid, assert_success=False)
            self.enter_duo_passcode(self.browser, assert_success=False)
            self.browser.switch_to.default_content()
            self.browser.wait_for_tag('p', 'You are not authorized to access the application:')
