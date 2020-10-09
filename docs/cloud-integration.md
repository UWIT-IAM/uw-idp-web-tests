# Cloud Products

This test suite requires both [Google Cloud Products](https://console.cloud.google.com/home/dashboard?project=uwit-mci-iam) 
and [AWS](https://idp.u.washington.edu/idp/profile/SAML2/Unsolicited/SSO?providerId=urn:amazon:webservices) access credentials.


## AWS 

These tests rely on test service providers (SPs) to validate behaviors. These SPs run on AWS EC2 instances. Because
they are only needed for these tests, they do not run all the time. Therefore the test environment needs to be able
to turn these instances on and off, so that humans don't have to.

## Google Cloud Products (GCP)

GCP is used to upload test artifacts ("webdriver reports") as well as secrets (namely, test identity credentials). 
Developers with requisite permissions can access and edit those secrets
[here](https://console.cloud.google.com/security/secret-manager/secret/idp-web-test-config?project=uwit-mci-iam).


# AWS & GCP Programmatic Access Keys

## GCP

*[REQUIRED]*

In order to run these tests, you must have a `GOOGLE_APPLICATION_CREDENTIALS` environment variable set. The variable
needs to point to the `/path/to/some.json`; the JSON file must have been downloaded from GCP after creating a Service Account.

This file should be unique to every user, and should not be shared. 

### Creating a Service Account

If you are an IAM developer with access to our GCP Aux. project, you can create a service account yourself. Otherwise,
have someone with access do this for you and send you the JSON. This credential file cannot be retrieved; if you lose it,
another one must be created, and the original revoked.

This is a **one-time requirement**.

1. Log in to GCP using the link in the first section of this document.
2. In the search bar, type "Service Accounts"; click the entry that reads "Service Accounts."
3. Click on "+ Create Service Account"
4. Fill in the form:
  - [Service account name]  "uwit-iam-dev-${YOUR_NETID}"
  - [Service account ID]  "uwit-iam-dev-${YOUR_NETID}"
  - [Service account description] "Developer access to the IAM GCP Aux. project."
5. Click "Continue"
6. On the next page, add the following roles:
  - Secret Manager Secret Accessor
  - Secret Manager Secret Version Manager  (because that's not confusing at all)
  - Storage Object Viewer
7. Click "Continue"
8. Click "Done." You will be taken back to to the service account listing.
9. Locate and click on the service account you just created.
10. Under "Keys," click "ADD KEY" => "Create new key." Select JSON. 
11. Download this key to your machine; you should only ever have to do this once, 
so put this somewhere central and permanent.

It is recommended to export this key as part of your terminal activation. Users on Linux or MacOS can run:

`echo "export GOOGLE_APPLICATION_CREDENTIALS=/path/to/some.json > ~/.bash_profile`

* `/path/to/some.json` should be replaced with the path to the JSON file you saved in step 11 above.
* `~/.bash_profile` may need to be replaced with `~/.bashrc`, `~/.zshrc` or some other name, depending on your 
personal terminal setup and preferences.
 
 
 ### AWS
 
 For programmatic access to AWS, you need to first log in to the AWS console using the link in the first 
 section of this document.
 
 If offered the option on sign in, choose "sandbox-iamteam."
 
 1. Click on "Services"
 1. Search for "IAM", and click on the entry.
 1. Click on "Users."
 1. Click "Add user."
 1. Fill in the form:
   - User name => your UW netid
   - Access type => Programmatic Access (Do _not_ select console management access!)
 1. Click "Next: Permissions"
 1. Click the box next to "idp-web-test-runners".
 1. Click "Next: Tags"
 1. Click "Next: Review"
 1. Click "Create user"
 1. Copy the access key id and paste it somewhere safe. (We'll come back to it in a minute.)
 1. Click "Show" under "Secret Access Key", copy it, and paste it somewhere safe.
   - **Make very sure you have pasted the secret access key; you won't be able to see it again.**
 1. Click "Close"
 
These should be exported as environment variables with the following names: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
You may also consider installing the AWS cli (`pip install awscli`) and running `aws config`, and pasting the entries there. 
Either option will work for Boto3, which creates AWS clients.
