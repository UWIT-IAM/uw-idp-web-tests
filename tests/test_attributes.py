"""
This set of tests is based on the manual tests found in the
IdP Release Candidate Test Matrix Version 4.2.4 (5/27/2021) here
https://wiki.cac.washington.edu/display/SMW/IAM+Team+Wiki

ATT-1 thru ATT-28.
"""

from webdriver_recorder.browser import Chrome
from tests.helpers import Locators
from tests.models import ServiceProviderInstance


def test_attributes(browser, netid, utils, sp_url, sp_domain, secrets, test_env):
    """
    Attribute release. SAML Tracer or similar can also be used to inspect these attribute values
    ATT-1 thru ATT-28
    """
    fresh_browser = Chrome()
    login = netid
    password = secrets.test_accounts.password
    sp = ServiceProviderInstance.diafine6
    idpenv = ''
    if test_env == "eval":
        idpenv = ":eval"

    attributes_to_test = {
        'cn': 'Lucy Mary Cartier',
        'displayName': 'Lucy Mary Cartier',
        'displayNameAndPronouns': 'Lucy Mary Cartier (they/them/theirs)',
        'eduPersonAffiliation': 'student;member;staff;employee',
        'eduPersonEntitlement': 'urn:mace:dir:entitlement:common-lib-terms;urn:mace:incommon:entitlement:common:1',
        'eduPersonPrincipleName': 'sptest01@washington.edu',
        'eduPersonScopedAffiliation': 'employee@washington.edu;student@washington.edu;staff@washington.edu;member@washington.edu',
        'eduPersonTargetedID': f'urn:mace:incommon:washington.edu{idpenv}!https://diafine6.sandbox.iam.s.uw.edu'
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

    with utils.using_test_sp(sp):
        fresh_browser.set_window_size(1024, 768)
        # go to url to check saml properties
        # https://diafine6.sandbox.iam.s.uw.edu/shib{test_env}/server-vars.aspx
        fresh_browser.get(f'{sp_url(sp)}/shib{test_env}')
        fresh_browser.send_inputs(login, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        fresh_browser.get(f'{sp_url(sp)}/shib{test_env}/server-vars.aspx')
        fresh_browser.wait_for_tag('pre', 'cn')
        content = fresh_browser.find_element_by_tag_name('pre')
        content_clean = content.get_attribute('innerHTML')
        attribute_data = [item.strip() for item in content_clean.split("<br>")]

        # eduPersonScopedAffiliation is a unique case
        wanted_key = 'eduPersonScopedAffiliation'

        result = next(filter(lambda x: x.startswith(wanted_key), attribute_data))
        found_values = set(result.split("= ")[1].split(";"))

        for key, value in attributes_to_test.items():
            if key == wanted_key:
                assert found_values == {
                    'employee@washington.edu',
                    'student@washington.edu',
                    'staff@washington.edu',
                    'member@washington.edu',
                }, f'Unexpected attributes found in comparison with: {found_values}'
            else:
                # matches on exact string only. mail won't count as a match for uwEduEmail and uwEduEmail won't match
                # mail
                assert f'{key} = {value}' in attribute_data

        fresh_browser.close()
