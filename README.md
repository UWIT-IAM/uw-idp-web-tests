# UW IdP Web Tests

Contains a test suite for UW's identity provider, using mock Shibboleth service providers.

To run the tests from the Github UI, [start here](docs/github-actions.md#run-the-tests).

Other detailed information can be found in the [docs](docs) directory.

You only need to keep reading if you want more details on contributing to this
test suite or you want to run the test suite in some way other than via Github Actions.

## Quickstart

- Follow the [bare minimum setup instructions](#bare-minimum)
- Run `./scripts/run-tests.sh`

# Dev Environment Setup

## Bare Minimum 

**If you are new to maintaining or running these tests, you must start here!**

1\. Follow the instructions for creating a Google Service Account in 
[docs/cloud-integration](docs/cloud-integration.md#CreatingAServiceAccount) and ensure you are 
exporting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

2\. [Install docker](https://docs.docker.com/get-docker/) on your machine, 
    and make sure the docker daemon is running.

## For running locally (via poetry)

Only required if you need more than the docker functionality. 
For instance, if you want IDE integration and easier debugging, do this!

1\. [Install pyenv](https://github.com/pyenv/pyenv#installation) (if you haven't already)

```
type pyenv || echo 'You need to install pyenv'
```


2\. Install your desired python version (3.7.7 and/or 3.8.6 are recommended) using pyenv:

```
py_version=3.7.7
test -d $HOME/.pyenv/versions/$py_version || pyenv install $py_version
```

3\. [Install poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions) (if you haven't already):

```
type poetry || echo 'You need to install poetry'
```


4\. Create your poetry virtualenv:

```
poetry env use ~/.pyenv/versions/$py_version/bin/python
poetry install
```

5\. Install chromedriver

You must run this step periodically, as Chrome and the installed chromedriver will
drift out of sync. 

To install chromedriver, run these commands in your terminal:

*Mac users*: 

```
export CHROMEDRIVER_DIST=mac64
```

*All users*:

```
export CHROMEDRIVER_DIR=$(poetry env list --full-path | head -n 1 | cut -f1 -d' ')/bin
bash <(curl -s https://raw.githubusercontent.com/UWIT-IAM/webdriver-recorder/master/bootstrap_chromedriver.sh)
```

# Running tests

See [docs/settings-and-options](docs/settings-and-options.md)
for more information on configuring your test environment.

Please keep in mind that the default options will take a few minutes to start due to cold start delays for our
[test service providers](docs/test-service-providers.md).


## Via docker

```
./scripts/run-tests.sh
```

You can pass additional arguments to pytest using the 
special `--` and `+-` arguments, example:

`--` will replace all default environment variables; `+-` will append to default 
variables. (Use this if you want nice log output).

**Example using `--`:**

```
./scripts/run-tests.sh -- --maxfail 1 tests/test_2fa_duo.py
# ...
# will output something like:
 Running pytest with args: --maxfail 1 tests/test_2fa_duo.py
```

**Example using `+-`:**
```
./scripts/run-tests.sh +- --settings-profile in_development tests/test_attributes.py
# ...
# will output something like: 
Running pytest with args: -o log_cli=true -o log_cli_level=info --settings-profile in_development tests/test_attributes.py
```

For more information, run `./scripts/run-tests.sh --help`


## Via virtualenv

```
poetry run pytest
```

## Via pycharm

If you are using Pycharm, make sure to:

- install the poetry plugin
-  configure your project to use the poetry environment 
- set 'pytest' as your project's test framework.

You should then be able to run and debug the tests easily from your IDE.

---

# Writing tests

We use [pytest](https://pytest.org) as our testing framework. Refer to pytest documentation for deep details about 
what you can do.

Here are some general tips:

1\. Create new files to represent collections of related tests.
2\. Your file names need to start with `test_` in order for pytest to collect them as part of your test suite.
3\. Your test functions need to start with `test_` in order for pytest ro run them as part of your test suite.
4\. Your class names need to start with `Test` in order for pytest to run them as part of your test suite.


# Helpful Links

- [IAM AWS Documentation](https://wiki.cac.washington.edu/pages/viewpage.action?pageId=85600799)
- [AWS Sign In Link for IAM devs](https://idp.u.washington.edu/idp/profile/SAML2/Unsolicited/SSO?providerId=urn:amazon:webservices)
- [Test Service Providers](https://wiki.cac.washington.edu/display/SMW/Test+Service+Providers)
- [Starting and Stopping Test SPs in AWS](https://wiki.cac.washington.edu/display/SMW/Starting+and+Stopping+a+Test+SP+in+AWS)
- [AWS EC2 Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html)
- [AWS Route53 Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html)
