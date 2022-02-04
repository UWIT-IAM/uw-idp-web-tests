# Generating Sustained Requests

You can also generate login attempts from many different clients using
Github Actions. This simply logs in to the UW Directory using the prod IDP.
You may provide a specific IdP to route traffic through.

While you _can_ run this from a bash terminal 
(`./scripts/run-login-request-generator.sh`), this will only generate
requests from a single IP address. 

## Running from Github Actions

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

## Running from the CLI

To run this locally using docker compose, you can just execute the
bash helper script:

```
./scripts/run-idp-login-request-generator.sh
```

Use the `--help` flag for a menu of options that can be provided.

Just remember that this will only generate requests from _your_ host.
