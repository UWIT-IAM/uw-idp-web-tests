# Running this test suite from Github Actions

- Go to the [workflow].
- Click on 'Run Workflow'
- Fill in the values as needed. (See [options](#options))
- Click on the second (green) "Run Workflow" button at the bottom of the form
  

## Options

### `target-idp-env`

Options are `eval` (default) and `prod`. This is the IdP you will be testing.

### `target-idp-host`

*Optional*. The short name of an IdP host you want to route all the test traffic to, 
e.g., `idp11` or `idpeval01`.

### `reason`

*Optional*. A short message indicating why you are running this test. For instance, 
if running for an RFC, adding a link to the RFC under the reason might be helpful.


### `pytest-args`

*Optional*. Any additional arguments you want to supply to pytest. Anything here 
will be added to the default pytest arguments.

**Note**. If you will be running the action more than once, for instance, to debug 
something, you might prefer to include the argument 
`--skip-test-service-provider-stop`, which will make subsequent runs faster by not 
shutting down the test SP's. Just try to remember to run normally once so that the 
test SPs will be shut down when you're done!

### `slack-channel`

The channel you want to send output to. This channel must have invited the Github 
Actions Crier (`/invite @iam-github-actions-crier`).


[workflow]: https://github.com/UWIT-IAM/uw-idp-web-tests/actions/workflows/automated-idp-web-tests.yml
