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
        fresh_browser.get(f'{sp_url(sp)}/shibprod')
        fresh_browser.send_inputs(login, password)
        fresh_browser.click(Locators.submit_button)
        fresh_browser.wait_for_tag('h2', f'{sp_domain(sp)} sign-in success!')

        # response = requests.get(f'{sp_url(sp)}/shibprod')
        # print('os.environ.keys()=', os.get)
        # print('response.status_code=', response.status_code)
        # print('response.headers=', response.headers['Content-Type'])
        fresh_browser.close()
