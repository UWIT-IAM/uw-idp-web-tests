from typing import Callable, NoReturn

import pytest
from webdriver_recorder.browser import BrowserRecorder

from tests.helpers import WebTestUtils
from tests.models import ServiceProviderInstance


class AccessControlTestBase:
    """
    Base class for the access_control suite which sets up some common fixtures
    and declares types for IDE hinting.
    """

    # These are just type declarations.
    # Do not set values on these fields!
    browser: BrowserRecorder
    utils: WebTestUtils
    sp_domain: Callable[[ServiceProviderInstance], str]
    password: str
    passcode: str
    test_env: str
    enter_duo_passcode: Callable[..., NoReturn]
    log_in_netid: Callable[..., NoReturn]
    sp_shib_url: Callable[..., str]

    @pytest.fixture(autouse=True)
    def initialize_base(
            self,
            utils,
            secrets,
            sp_url,
            test_env,
            sp_domain,
            enter_duo_passcode,
            log_in_netid,
            sp_shib_url,
            fresh_browser,
    ):
        self.browser = fresh_browser
        self.utils = utils
        self.sp_domain = sp_domain
        self.password = secrets.test_accounts.password.get_secret_value()
        self.passcode = secrets.test_accounts.duo_code.get_secret_value()
        self.test_env = test_env
        self.enter_duo_passcode = enter_duo_passcode
        self.log_in_netid = log_in_netid
        self.sp_shib_url = sp_shib_url
