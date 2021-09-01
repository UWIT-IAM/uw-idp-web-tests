"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

NID-1 thru NID-2.
"""
from typing import Optional

from tests.models import ServiceProviderInstance
from webdriver_recorder.browser import Chrome
from tests.attributes import AttributeReleaseTestBase


class TestUniqueAttributes(AttributeReleaseTestBase):
    browser: Chrome

    def check_attribute(self, get_fresh_browser, test_sp, test_netid, attribute_to_test,
                              assert_success: Optional[bool] = None):
        with get_fresh_browser() as new_browser:
            self.attribute_value = self._find_attributes(test_sp, test_netid,
                                                         attribute_to_test,
                                                         new_browser=new_browser,
                                                         assert_success=assert_success)
            return self.attribute_value

    def test_unique_transientid(self, netid, get_fresh_browser):
        """
        NameID release NID-1, transientid unique every time
        """
        sp = ServiceProviderInstance.diafine6
        attribute_to_test = 'MappingNameID-transient'

        unique_transientid1 = self.check_attribute(get_fresh_browser, sp, netid, attribute_to_test)
        unique_transientid2 = self.check_attribute(get_fresh_browser, sp, netid, attribute_to_test)

        assert not (unique_transientid1 == unique_transientid2)

    def test_persistentid(self, get_fresh_browser, netid3):
        """
        NameID release NID-2, persistent id unique on same diafine, non-unique across diafines
        """
        sp7 = ServiceProviderInstance.diafine7
        sp12 = ServiceProviderInstance.diafine12
        attribute_to_test = 'MappingNameID-persistent'

        persistentid_sp7_1 = self.check_attribute(get_fresh_browser, sp7, netid3, attribute_to_test, assert_success=False)
        persistentid_sp7_2 = self.check_attribute(get_fresh_browser, sp7, netid3, attribute_to_test, assert_success=False)
        persistentid_sp12 = self.check_attribute(get_fresh_browser, sp12, netid3, attribute_to_test)

        assert (persistentid_sp7_1 == persistentid_sp7_2)
        assert not (persistentid_sp12 == persistentid_sp7_1)



