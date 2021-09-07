import json
import logging
from typing import Callable, NoReturn, Dict, List, Optional

import pytest
from webdriver_recorder.browser import BrowserRecorder

from tests.helpers import WebTestUtils


class AttributeReleaseTestBase:
    # These are just type declarations.
    # Do not set values on these fields!
    fresh_browser: BrowserRecorder
    login: str
    utils: WebTestUtils
    sp_shib_url: Callable[..., str]
    test_env: str
    enter_duo_passcode: Callable[..., NoReturn]
    log_in_netid: Callable[..., NoReturn]
    idp_env: str

    @pytest.fixture(autouse=True)
    def initialize_base(
            self,
            netid,
            utils,
            sp_shib_url,
            test_env,
            log_in_netid,
            enter_duo_passcode,
    ):
        self.login = netid
        self.utils = utils
        self.sp_shib_url = sp_shib_url
        self.log_in_netid = log_in_netid
        self.enter_duo_passcode = enter_duo_passcode

        self.idp_env = ''
        if test_env == "eval":
            self.idp_env = ":eval"

    def _parse_line(self, line):
        parts = line.split('= ', maxsplit=1)
        if len(parts) == 1:
            parts.append('')
        return tuple(map(lambda p: p.strip(), parts))

    def _get_attribute_data(self, url, new_browser: Optional[BrowserRecorder] = None) -> Dict[str, str]:
        if new_browser is not None:
            browser = new_browser
        else:
            browser = self.fresh_browser

        browser.get(f'{url}/server-vars.aspx')
        content: List[str] = list(
            filter(bool, browser.wait_for_tag('pre', 'cn').text.split("\n"))
        )

        attribute_data = {  # Key-value dict of all attributes...
            k.strip(): v.strip() for k, v in map(self._parse_line, content)
        }
        logging.debug(f"Parsed attribute data: {json.dumps(attribute_data, indent=4)}")
        return attribute_data

    def _find_attributes(self, test_sp, test_netid, test_attributes, new_browser: Optional = None, assert_success: Optional[bool] = None, undefined_order_keys: Optional = None):
        """
        For test_attributes, a string type means there is only one attribute to check,
        anything else is treated like one or more attributes to check
        """
        if new_browser is not None:
            browser = new_browser
        else:
            browser = self.fresh_browser

        with self.utils.using_test_sp(test_sp):
            browser.set_window_size(1024, 768)
            # go to url to check saml properties
            # https://diafineX.sandbox.iam.s.uw.edu/shib{test_env}/server-vars.aspx
            url = self.sp_shib_url(test_sp)
            browser.get(url)

            self.log_in_netid(browser, test_netid, assert_success=assert_success)
            if assert_success is False:
                self.enter_duo_passcode(browser, match_service_provider=test_sp)

            if isinstance(test_attributes, str):
                actual_data = self._get_attribute_data(url, browser)
                key = test_attributes
                actual = actual_data.get(key)
                return actual
            else:
                actual_data = self._get_attribute_data(url, browser)
                for key, value in test_attributes.items():
                    if undefined_order_keys is not None and key in undefined_order_keys:
                        target_values = set(value.split(';'))
                        found_values = set(actual_data.get(key, '').split(';'))
                        assert found_values == target_values, \
                            f'For key {key}, expected values: {target_values} but found {found_values}'
                    else:
                        actual = actual_data.get(key)
                        assert actual == value, f'For key {key}, expected value "{value}" but got "{actual}"'

