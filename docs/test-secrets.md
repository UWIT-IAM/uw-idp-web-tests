# Test Secrets

These tests rely on test identities with actual credentials. Even though they are test credentials, we do not 
want those committed to any repository, because they could be used for nefarious purposes by bad actors.

So, these credentials are kept in Google Secret Manager.

Right now, all test identities have the same password and duo code. If we want to support different values for each,
we will need to do some slight refactoring.

## Updating secrets

To update secrets, you can use the CLI utility to download the existing secrets as JSON, and edit that JSON, and 
then re-publish them.

```bash
python -m tests.secret_manager download --filename my-secrets.json  # defaults to secrets.json
```

will download the secrets to the filename indicated. 

```bash
python -m tests.secret_manager publish --filename my-secrets.json # required; does not assume a default.
```

will publish secrets from the filename to Google Secret Manager. Because publishing new secrets will take effect 
immediately for all consumers, it is recommended to test against them before publishing.

## Testing secrets

If you want to test a local copy of the secrets file, you can use `--use-local-secrets`. By default, this will 
look for `secrets.json` in your working directory, but you can set an absolute path by also adding 
`--local-secrets-filename /path/to/my-secrets.json`.


# Using the Google Console

If you need or want to look at this secret from the GCP Console:

1. Log in to https://console.cloud.google.com
2. Select our auxiliary project
3. Search for "Secret Manager" (or click on the hamburger menu => Security => Secret Manager)
4. Click on "idp-web-test-config"