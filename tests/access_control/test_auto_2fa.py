from tests.access_control import AccessControlTestBase
from tests.models import ServiceProviderInstance


class TestAuto2fa(AccessControlTestBase):
    def test_auto_2fa_a(self, netid3):
        """
        AC-1 Part A
        """
        # Prompted for pwd then 2FA on diafine7.
        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, netid3, assert_success=False)
            self.enter_duo_passcode(self.browser)

    def test_auto_2fa_b(self, netid3):
        """
        AC-1 Part B
        """
        # b. Prompted for 2FA only on diafine7.
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, netid3, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

    def test_auto_2fa_c(self, netid3):
        """
        AC-1 Part C
        """
        # Prompted for pwd then 2FA on diafine7.
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            with self.browser.tab_context():
                self.browser.get(self.sp_shib_url(sp))
                self.log_in_netid(self.browser, netid3, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            with self.browser.tab_context():
                self.browser.get(self.sp_shib_url(sp, append='force'))
                self.log_in_netid(self.browser, netid3, match_service_provider=sp, assert_success=False)
                self.enter_duo_passcode(self.browser)

    def test_auto_2fa_d(self, netid3):
        """
        AC-1 Part D
        """
        # d. No prompts on diafine7.
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, netid3, match_service_provider=sp, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_auto_2fa_e(self, netid3):
        """
        AC-1 Part E
        """
        # Prompted for pwd then 2FA on diafine7.
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, netid3, match_service_provider=sp, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfaforce'))
            self.log_in_netid(self.browser, netid3, match_service_provider=sp, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp, is_this_your_device_screen=False)

    def test_auto_2fa_f(self, netid3):
        """
        AC-1 Part F
        """
        # f. Start new 2FA session at https://diafine7.sandbox.iam.s.uw.edu/shibevalmfa.
        # Close browser.
        # Prompted for pwd then 2FA on diafine7 (no 500 error).
        sp = ServiceProviderInstance.diafine7
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='mfa'))
            self.log_in_netid(self.browser, netid3, match_service_provider=sp, assert_success=False)
            self.enter_duo_passcode(self.browser, match_service_provider=sp)
