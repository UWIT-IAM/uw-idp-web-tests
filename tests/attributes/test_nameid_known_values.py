"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

NID-3 thru NID-5.
"""

from tests.attributes import AttributeReleaseTestBase

import pytest

from tests.models import ServiceProviderInstance
from webdriver_recorder.browser import Chrome


class TestAttributes(AttributeReleaseTestBase):
    browser: Chrome

    @pytest.fixture(autouse=True)
    def initialize(self, fresh_browser):
        self.fresh_browser = fresh_browser

    def test_nameid_eppn_attributes(self):
        sp = ServiceProviderInstance.diafine8

        attributes_to_test_eppnnameid = {
            'MappingNameID-eppn': f'urn:mace:incommon:washington.edu{self.idp_env}!!https://diafine8.sandbox.iam.s.uw.edu/shibboleth!!sptest01@washington.edu'
        }

        self._find_attributes(sp, self.login, attributes_to_test_eppnnameid)

    def test_nameid_idnameid_attributes(self, netid7):
        sp = ServiceProviderInstance.diafine9

        attributes_to_test_idnameid = {
            'MappingNameID-idnameid': f'urn:mace:incommon:washington.edu{self.idp_env}!!https://diafine9.sandbox.iam.s.uw.edu'
                                      '/shibboleth!!sptest07'
        }

        self._find_attributes(sp, netid7, attributes_to_test_idnameid)

    def test_nameid_uweduemailnameid_attributes(self, netid7, enter_duo_passcode):
        sp = ServiceProviderInstance.diafine10

        attributes_to_test_uweduemailnameid = {
            'MappingNameID-eduemail': f'urn:mace:incommon:washington.edu{self.idp_env}!!https://diafine10.sandbox.iam.s.uw.edu'
                                      '/shibboleth!!sptest07@uw.edu'
        }
        self._find_attributes(sp, netid7, attributes_to_test_uweduemailnameid,
                              assert_success=False)
