# UW IdP Web Tests

Contains a test suite for UW's identity provider, using mock Shibboleth service providers.

Detailed information can be found in the `docs/` directory.

# Dev Environment Setup

**If you are new to maintaining or running these tests, you must start here!**

This quick-start guide will get you up and running, but assumes you already have a python 3.7+ executable already 
on your system. If you are new to python environments, you might want to follow 
[this guide](https://wiki.cac.washington.edu/display/~goodtom@washington.edu/Installing+and+Configuring+Python+for+Development)
to make sure you install python _and_ pip in a safe, sandboxable way.

The below instructions will assume that `python3` (and its partner, `pip3`) 
is an alias to the python interpreter binary you want to develop against.

1\. Make sure you have `virtualenv` installed: `pip install virtualenv` 
(if you followed the above instructions, you can skip this step)
2\. Clone this repository:

`git clone git@github.com:UWIT-IAM/uw-idp-web-tests`

3\. Create a virtual environment: `cd uw-idp-web-tests && virtualenv --python /path/to/your/python3.7 venv`

This will create the `venv` directory under `uw-idp-web-tests`.

4\. Activate your environment: `source venv/bin/activate`

5\. Install dependencies: `pip install -r requirements.txt`

6\. Install Chromedriver: Follow the instructions from the [webdriver-recorder](https://github.com/uwit-iam/webdriver-recorder#installing-and-configuring-the-chromedriver) 
package, _or_ just copy the [bootstrap-chromedriver.sh](https://github.com/UWIT-IAM/webdriver-recorder/blob/master/bootstrap_chromedriver.sh) script.

If you use the script, make sure to set `CHROMEDRIVER_DIR=venv/bin`. 

7\. Follow the instructions for creating a Google Service Account in 
[docs/cloud-integration](docs/cloud-integration.md#CreatingAServiceAccount) and ensure you are 
exporting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

## Readiness check

If you see any errors or warning output when running the below commands, something is wrong. (*unless you know better)

```bash
source venv/bin/activate
which chromedriver 2>/dev/null || echo "Chromedriver is not available in your virtualenv"
test -z ${GOOGLE_APPLICATION_CREDENTIALS} && echo "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set."
```

# Running tests

To run these tests, simply issue the `pytest` command. See [docs/settings-and-options](docs/settings-and-options.md) 
for more information on configuring your test environment.

Please keep in mind that the default options will take a few minutes to start due to cold start delays for our 
[test service providers](docs/test-service-providers.md).

# Writing tests

We use [pytest](https://pytest.org) as our testing framework. Refer to pytest documentation for deep details about 
what you can do.

Here are some general tips:

1\. Create new files to represent collections of related tests.
2\. Your file names need to start with `test_` in order for pytest to collect them as part of your test suite.
3\. Your test functions need to start with `test_` in order for pytest ro run them as part of your test suite.


# Helpful Links

- [IAM AWS Documentation](https://wiki.cac.washington.edu/pages/viewpage.action?pageId=85600799)
- [AWS Sign In Link for IAM devs](https://idp.u.washington.edu/idp/profile/SAML2/Unsolicited/SSO?providerId=urn:amazon:webservices)
- [Test Service Providers](https://wiki.cac.washington.edu/display/SMW/Test+Service+Providers)
- [Starting and Stopping Test SPs in AWS](https://wiki.cac.washington.edu/display/SMW/Starting+and+Stopping+a+Test+SP+in+AWS)
- [AWS EC2 Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html)
- [AWS Route53 Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html)