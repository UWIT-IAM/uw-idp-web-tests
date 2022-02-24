import time

from webdriver_recorder.browser import Locator, By


def test_make_continuous_requests(request, browser, netid, secrets):
    """
    By default this test will exit successfully without doing anything.
    Test runners must set "--lb-num-loops" in order for this test to
    do anything.
    """
    num_loops = int(request.config.getoption('lb_num_loops', default=0))
    sleep_time = int(request.config.getoption('lb_sleep_time', default=60))

    def log_in_user():
        browser.get('https://directory.uw.edu/saml/login')
        try:  # User may not be prompted to sign in, that's OK, we're still going through the IdP
            browser.click(Locator(
                search_method=By.ID,
                search_value='weblogin_netid',
            ))
            browser.send_inputs(
                netid,
                secrets.test_accounts.password.get_secret_value(),
            )
            browser.click(Locator(
                search_method=By.ID,
                search_value='submit_button',
            ))
        except Exception:
            browser.snap()
        finally:
            try:  # The population-option-all element is only present when a user is signed in
                browser.wait_for(Locator(
                    search_method=By.ID,
                    search_value='population-option-all',
                ))
            except Exception:
                browser.snap()
                pass

    def log_out_user():
        browser.get('https://directory.uw.edu/saml/logout')
        browser.snap()

    for _ in range(num_loops):
        log_in_user()
        log_out_user()
        time.sleep(sleep_time)
