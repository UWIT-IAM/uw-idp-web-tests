import json
import logging
from typing import Dict, List, Tuple, Optional

import pytest

from tests.models import ServiceProviderInstance
from webdriver_recorder.browser import Chrome


class TestUniqueAttributes:
    browser: Chrome

    @pytest.fixture(autouse=True)
    def initialize(self, utils, sp_shib_url, sp_domain, test_env, log_in_netid, enter_duo_passcode):
        self.utils = utils
        self.sp_shib_url = sp_shib_url
        self.log_in_netid = log_in_netid
        self.enter_duo_passcode = enter_duo_passcode
        self.unique_transientid1 = ''
        self.unique_transientid2 = ''
        self.persistentid_1 = ''
        self.persistentid_2 = ''

        self.idp_env = ''
        if test_env == "eval":
            self.idp_env = ":eval"

    def _parse_line(self, line):
        parts = line.split('= ', maxsplit=1)
        if len(parts) == 1:
            parts.append('')
        return tuple(map(lambda p: p.strip(), parts))

    def _get_attribute_data(self, new_browser, url) -> Dict[str, str]:
        new_browser.get(f'{url}/server-vars.aspx')
        content: List[str] = list(
            filter(bool, new_browser.wait_for_tag('pre', 'cn').text.split("\n"))
        )
        attribute_data = {  # Key-value dict of all attributes...
            k.strip(): v.strip() for k, v in map(self._parse_line, content)
        }
        logging.debug(f"Parsed attribute data: {json.dumps(attribute_data, indent=4)}")
        return attribute_data

    def _find_attributes(self, test_sp, test_netid, test_attribute, new_browser, assert_success: Optional[bool] = None):
        with self.utils.using_test_sp(test_sp):
            url = self.sp_shib_url(test_sp)
            new_browser.set_window_size(1024, 768)
            new_browser.get(url)

            self.log_in_netid(new_browser, test_netid, assert_success=assert_success)
            if assert_success is False:
                self.enter_duo_passcode(new_browser, match_service_provider=test_sp)

            actual_data = self._get_attribute_data(new_browser, url)
            key = test_attribute
            actual = actual_data.get(key)
            return actual

    def test_check_unique_transientid(self, netid, get_fresh_browser, utils, sp_shib_url, log_in_netid):
        sp = ServiceProviderInstance.diafine6
        attribute_to_test = 'MappingNameID-transient'

        with get_fresh_browser() as new_browser:
            self.unique_transientid1 = self._find_attributes(test_sp=sp, test_netid=netid, test_attribute=attribute_to_test, new_browser=new_browser)
        with get_fresh_browser() as new_browser:
            self.unique_transientid2 = self._find_attributes(test_sp=sp, test_netid=netid, test_attribute=attribute_to_test, new_browser=new_browser)
            assert not (self.unique_transientid1 == self.unique_transientid2)

    def test_check_equal_persistentid(self, get_fresh_browser, netid3):
        sp = ServiceProviderInstance.diafine7
        attribute_to_test = 'MappingNameID-persistent'

        with get_fresh_browser() as new_browser:
            self.persistentid_1 = self._find_attributes(test_sp=sp, test_netid=netid3, test_attribute=attribute_to_test, new_browser=new_browser, assert_success=False)
        with get_fresh_browser() as new_browser:
            self.persistentid_2 = self._find_attributes(test_sp=sp, test_netid=netid3, test_attribute=attribute_to_test, new_browser=new_browser, assert_success=False)
            assert (self.persistentid_1 == self.persistentid_2)

