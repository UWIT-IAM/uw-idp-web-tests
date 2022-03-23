# On-Demand Github Actions Workflows

You can perform a number of actions directly from this
repository's [Github Actions UI]:

- [Run the tests](#run-the-tests)
- [Turn off the test SPs](#turn-off-the-test-service-providers)
- [Generate IdP login requests](#generate-idp-login-requests)
- [Re-build and re-cache the docker image](#re-build-and-re-cache-the-testing-docker-image)

From the Actions UI, you can click on any workflow and then the "Run Workflow" button
to get started. If a particular workflow does not have a "Run Workflow" button,
it is not meant to be executed manually.

After clicking the "Run Workflow" button, you will be given the opportunity to 
select a branch and (maybe) fill in some other options. Unless you are testing 
a change to the workflow itself, you should leave the branch set to `mainline`.

## Run the tests
 
[Link to workflow](https://github.com/UWIT-IAM/uw-idp-web-tests/actions/workflows/automated-idp-web-tests.yml)

**If you run this workflow manually, please also [turn off the test SP's when you 
are done](#turn-off-the-test-service-providers-sps)!**

These tests are run automatically each day, but you can execute them at any time
and configure certain options to meet your testing needs.

### Test run options

#### `target-idp-env`

Options are `eval` (default) and `prod`. This is the IdP you will be testing.

#### `target-idp-host`

*Optional*. The short name of an IdP host you want to route all the test traffic to,
e.g., `idp11` or `idpeval01`.

#### `reason`

*Optional*. A short message indicating why you are running this test. For instance,
if running for an RFC, adding a link to the RFC under the reason might be helpful.


#### `pytest-args`

*Optional*. Any additional arguments you want to supply to pytest. Anything here
will be added to the default pytest arguments.

**Note**. If you will be running the action more than once, for instance, to debug
something, you might prefer to include the argument
`--skip-test-service-provider-stop`, which will make subsequent runs faster by not
shutting down the test SP's. Just try to remember to run normally once so that the
test SPs will be shut down when you're done!

#### `slack-channel`

The channel you want to send output to. This channel must have invited the Github
Actions Crier (`/invite @iam-github-actions-crier`).

## Turn off the test Service Providers (SP's)

The test SP's are turned on at the start of testing, but 
are not turned off by tests, due to complexity with overlapping
test runs. Therefore, they are turned off twice a day automatically 
(after the early morning scheduled runs, and after the end of the work day).

You can turn off the test SP's by executing the 
[workflow](https://github.com/UWIT-IAM/uw-idp-web-tests/actions/workflows/stop-test-service-providers.yml)
.

There are no additional options here. Just click the button and go.

## Generate IdP login requests

To generate requests from multiple IP addresses, you can use the
[IdP Login Request Generator Workflow](https://github.com/UWIT-IAM/uw-idp-web-tests/actions/workflows/idp-login-request-generator.yml).

Click the "Run Workflow" button. You will be presented with a form to configure
the number of login attempts per host, and the wait time between login attempts.

The number of hosts is fixed, but can be changed by updating the workflow in a
separate branch, then selecting that branch on the form. (Otherwise, you should
always run this with the default branch selected).

The IP addresses for the test runners will be available in the action run summary,
and the webdriver-report screenshots will also be included as artifacts in the same
summary.

## Re-build and re-cache the testing docker image


[test workflow]: https://github.com/UWIT-IAM/uw-idp-web-tests/actions/workflows/automated-idp-web-tests.yml
[Github Actions UI]: https://github.com/uwit-iam/uw-idp-web-tests/actions
