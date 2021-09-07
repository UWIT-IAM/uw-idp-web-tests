"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

ATT-1 thru ATT-28.
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

    def test_attributes(self):
        attributes_to_test = {
            'cn': 'Lucy Mary Cartier',
            'displayName': 'Lucy Mary Cartier',
            'displayNameAndPronouns': 'Lucy Mary Cartier (they/them/theirs)',
            'eduPersonAffiliation': 'student;member;staff;employee',
            'eduPersonEntitlement': 'urn:mace:dir:entitlement:common-lib-terms;urn:mace:incommon:entitlement:common:1',
            'eduPersonPrincipleName': 'sptest01@washington.edu',
            'eduPersonScopedAffiliation': 'employee@washington.edu;student@washington.edu;staff@washington.edu;member@washington.edu',
            'eduPersonTargetedID': f'urn:mace:incommon:washington.edu{self.idp_env}!https://diafine6.sandbox.iam.s.uw.edu'
                                   f'/shibboleth!22d186bb38a02d3ef949f9555156947f',
            'employeeNumber': '000211350',
            'givenName': 'Lucy Mary',
            'homeDepartment': '.TEST',
            'isMemberOf': 'urn:mace:washington.edu:groups:uw_iam_sp-test-groups_test-users;urn:mace:washington.edu:groups:uw_iam_sp-test-groups_test-users_subgroup',
            'mail': 'sptest01@uw.edu',
            'mailstop': '359540',
            'phone': '+1 206 123-4567',
            'preferredFirst': 'Lucy',
            'preferredMiddle': 'Mary',
            'preferredSurname': 'Cartier',
            'registeredGivenName': 'Lucretia',
            'registeredSurname': 'Carter',
            'surname': 'Cartier',
            'title': 'Crash Test Dummy',
            'uwEduEmail': 'sptest01@uw.edu',
            'uwNetID': 'sptest01',
            'uwPronouns': 'they/them/theirs',
            'uwRegID': '6D99B6F8FB52F3B5A334175D689F6136',
            'uwStudentID': '9780200',
            'uwStudentSystemKey': '990200200'
        }

        undefined_order_keys = {  # These keys multiple values in an undefined order
            'eduPersonAffiliation', 'eduPersonEntitlement', 'eduPersonScopedAffiliation', 'isMemberOf'
        }

        sp = ServiceProviderInstance.diafine6
        self._find_attributes(sp, self.login, attributes_to_test, undefined_order_keys=undefined_order_keys)


