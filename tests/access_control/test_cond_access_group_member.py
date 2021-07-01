import pytest

from tests.access_control import AccessControlTestBase
from tests.models import ServiceProviderInstance


class TestCondAccessGroupMember(AccessControlTestBase):
    @pytest.fixture(autouse=True)
    def initialize(self, netid7):
        """
        AC-3.1	Conditional access, tester is group member.
        diafine9, sptest07
        """
        self.netid = netid7

    def test_a(self):
        """
        a. Prompted for pwd on diafine9.
        """
        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_b(self):
        """
        b. No prompts on diafine9.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')

    def test_c(self):
        """
        c. Prompted for pwd on diafine9.
        """
        sp = ServiceProviderInstance.diafine6
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)

        sp = ServiceProviderInstance.diafine9
        with self.utils.using_test_sp(sp):
            self.browser.get(self.sp_shib_url(sp, append='force'))
            self.log_in_netid(self.browser, self.netid, match_service_provider=sp)
            self.browser.wait_for_tag('h2', f'{self.sp_domain(sp)} sign-in success!')
