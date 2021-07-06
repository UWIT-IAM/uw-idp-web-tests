"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

ATT-1 thru ATT-28.
"""
import json
import logging
from typing import Dict, List, Tuple

from selenium.webdriver.remote.webelement import WebElement

from tests.helpers import logger
from tests.models import ServiceProviderInstance


def test_attributes(browser, netid, utils, sp_shib_url, sp_domain, test_env, log_in_netid):
    """
    Attribute release. SAML Tracer or similar can also be used to inspect these attribute values
    ATT-1 thru ATT-28
    """
    login = netid
    sp = ServiceProviderInstance.diafine6
    idp_env = ''
    if test_env == "eval":
        idp_env = ":eval"

    attributes_to_test = {
        'cn': 'Lucy Mary Cartier',
        'displayName': 'Lucy Mary Cartier',
        'displayNameAndPronouns': 'Lucy Mary Cartier (they/them/theirs)',
        'eduPersonAffiliation': 'student;member;staff;employee',
        'eduPersonEntitlement': 'urn:mace:dir:entitlement:common-lib-terms;urn:mace:incommon:entitlement:common:1',
        'eduPersonPrincipleName': 'sptest01@washington.edu',
        'eduPersonScopedAffiliation': 'employee@washington.edu;student@washington.edu;staff@washington.edu;member@washington.edu',
        'eduPersonTargetedID': f'urn:mace:incommon:washington.edu{idp_env}!https://diafine6.sandbox.iam.s.uw.edu'
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
        'eduPersonAffiliation', 'eduPersonScopedAffiliation'
    }

    def _parse_line(line):
        parts = line.split('= ', maxsplit=1)
        if len(parts) == 1:
            parts.append('')
        return tuple(map(lambda p: p.strip(), parts))

    def _get_attribute_data() -> Dict[str, str]:
        browser.get(f'{url}/server-vars.aspx')
        content: List[str] = list(
            filter(bool, browser.wait_for_tag('pre', 'cn').text.split("\n"))
        )
        attribute_data = {  # Key-value dict of all attributes...
            k.strip(): v.strip() for k, v in map(_parse_line, content)
        }
        logging.debug(f"Parsed attribute data: {json.dumps(attribute_data, indent=4)}")
        return attribute_data

    with utils.using_test_sp(sp):
        browser.set_window_size(1024, 768)
        # go to url to check saml properties
        # https://diafine6.sandbox.iam.s.uw.edu/shib{test_env}/server-vars.aspx
        url = sp_shib_url(sp)
        browser.get(url)
        log_in_netid(browser, login)
        actual_data = _get_attribute_data()

        for key, value in attributes_to_test.items():
            if key in undefined_order_keys:
                target_values = set(value.split(';'))
                found_values = set(actual_data.get(key, '').split(';'))
                assert found_values == target_values, \
                    f'For key {key}, expected values: {target_values} but found {found_values}'
            else:
                actual = actual_data.get(key)
                assert actual == value, f'For key {key}, expected value "{value}" but got "{actual}"'
