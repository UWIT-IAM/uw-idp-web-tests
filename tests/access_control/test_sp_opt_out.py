from tests.access_control import AccessControlTestBase
from tests.models import ServiceProviderInstance


class TestSpOptOut(AccessControlTestBase):
    def test_a(self, netid3):
        """
        a. Prompted for pwd (SP opt-out trumps auto-2FA).
        """
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, netid3, match_service_provider=sp)

    def test_b(self, netid4):
        """
        b. Prompted for pwd (SP opt-out trumps user opt-in).
        """
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, netid4, match_service_provider=sp)

    def test_c(self, netid3):
        """
        c. Prompted for pwd, then 2FA (requested MFA authnContextClassRef trumps SP opt-out).
        """
        sp = ServiceProviderInstance.diafine12
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, netid3, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)
