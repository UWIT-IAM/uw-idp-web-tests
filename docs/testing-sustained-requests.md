# Generating Sustained Requests

You can also generate login attempts from many different clients using
Github Actions. This simply logs in to the UW Directory using the prod IDP.
You may provide a specific IdP to route traffic through.

While you _can_ run this from a bash terminal 
(`./scripts/run-login-request-generator.sh`), this will only generate
requests from a single IP address. 

## Running from Github Actions

Refer to [github-actions.md](github-actions.md#generate-idp-login-requests).
