from functools import partial
from urllib import request
import os

import pytest
import requests
from webdriver_recorder.browser import Chrome

from tests.helpers import CTRL_KEY, Locators, WebTestUtils
from tests.models import ServiceProviderInstance, AccountNetid, TestSecrets


@pytest.fixture
def browser() -> Chrome:
    return Chrome()


@pytest.fixture(scope='class')
def class_browser() -> Chrome:
    browser = Chrome()
    try:
        yield browser
    finally:  # Even if there is an error
        browser.close()


@pytest.fixture
def netid() -> str:
    return AccountNetid.sptest01.value


def test_attributes(browser, netid, utils, sp_url, sp_domain, secrets):
    fresh_browser = Chrome()
    login = netid
    password = secrets.test_accounts.password
    sp = ServiceProviderInstance.diafine6
    with utils.using_test_sp(sp):
        fresh_browser.get(f'{sp_url(sp)}/shibeval')
        fresh_browser.send_inputs(login, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')
        # go to url to check saml properties
        # https://diafine6.sandbox.iam.s.uw.edu/shibeval/server-vars.aspx
        fresh_browser.get(f'{sp_url(sp)}/shibprod/server-vars.aspx')
        element = fresh_browser.wait_for_tag('pre', f'{sp_domain(sp)}/')
        assert ('cn = Lucy Mary Cartier' in element.text)
        assert ('displayName = Lucy Mary Cartier' in element.text)
        assert ('affiliation = employee@washington.edu;student@washington.edu;staff@washington.edu;member@washington.edu'
                in element.text)
        assert ('entitlement = urn:mace:dir:entitlement:common-lib-terms;urn:mace:incommon:entitlement:common:1'
                in element.text)
        assert ('eppn = sptest01@washington.edu' in element.text)
        """
        These three attributes are not yet present
        eduPersonScopedAffiliation (scopedAffiliation)? - looks like eduPersonAffiliation (affiliation)
        eduPersonTargetedID (ePTID)?
        eduPersonTargetedID (attributePersistentID)?
        """
        assert ('employeeNumber = 000211350' in element.text)
        assert ('givenName = Lucy Mary' in element.text)
        assert ('homeDepartment = .TEST' in element.text)
        assert ('gws_groups = urn:mace:washington.edu:groups:uw_iam_sp-test-groups_test-users;urn:mace:washington.edu:groups:uw_iam_sp-test-groups_test-users_subgroup' in element.text)
        assert ('email = sptest01@uw.edu' in element.text)
        assert ('mailstop = 359540' in element.text)
        assert ('phone = +1 206 123-4567' in element.text)
        assert ('preferredFirst = Lucy' in element.text)
        assert ('preferredMiddle = Mary' in element.text)
        assert ('preferredSurname = Cartier' in element.text)
        assert ('registeredGivenName = Lucretia' in element.text)
        assert ('registeredSurname = Carter' in element.text)
        assert ('surname = Cartier' in element.text)
        assert ('title = Crash Test Dummy' in element.text)
        assert ('uwNetID = sptest01' in element.text)
        assert ('uwEduEmail = sptest01@uw.edu' in element.text)
        assert ('uwRegID = 6D99B6F8FB52F3B5A334175D689F6136' in element.text)
        assert ('uwStudentID = 9780200' in element.text)
        assert ('uwStudentSystemKey = 990200200' in element.text)
        fresh_browser.close()
