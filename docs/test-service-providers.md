# Test Service Providers (SPs)

Most of our documentation for the test service providers can be found [here](https://wiki.cac.washington.edu/display/SMW/Test+Service+Providers).

This document will cover how to turn them on and off again.

## Starting & Stopping SPs

### Eager SP Lifecycle Management

By default, these tests will turn on all SPs at the beginning of a test session, and turn 
them all off at the end of the session. This is convenient for the most common use case of 
running the entire test suite as a scheduled endeavor.

However, the tests don't know if anyone else is running tests at the same time. Therefore, if running
these manually, it might be a good idea to let the team know. The `#iam-accessmgmt` slack channel is a good place 
to do that. Otherwise, you may shut down the test SPs while someone else is trying to use them (or vice-versa).

### Lazy SP Lifecycle Management

If you only want to start instances that you need for some small subset of tests,
you can add the `--skip-test-service-provider-start` flag to your `pytest` command. 

When you do this, SPs are only started if they are encountered in a test. This is accomplished 
by adding the `with utils.using_test_sp` block to tests. The test suite maintains a map of known 
states, and will only start an SP if it is declared as required by the `with` block, and if it has 
not already been started.

Note that the AWS EC2 `start_instances` request is idempotent; if an instance is already active,
it won't do any harm to request it to start again.

At the end of your test session, all started instances will be turned off automatically.

### Keeping Instances Running

If you are actively working on this test suite, or trying to solve a problem, and are running these 
suites frequently, you can leave them on between test runs by adding the `--skip-test-service-provider-stop` flag 
to your `pytest` command.

This can greatly speed up testing, because you won't be waiting for cold starts and DNS propagation every time. However,
you must remember to turn the instances off at the end of the day. (You can do this via the CLI, or just run the tests 
without the above `--skip...` flag, to allow the test suite to turn them off for you.)


### Manual SP Lifecycle Management using the CLI

You can also manually activate or deactivate the test SPs using the light CLI.

`python -m tests.sp_manager start` will start all instances

`python -m tests.sp_manager stop` will stop all instances.

You can also specify the `-sp` flag to turn on or off specific instances. You must use that argument multiple times 
to specify more than one:

`python -m tests.sp_manager start -sp diafine6 -sp diafine12`


## Service Provider Resource Tags

AWS allows us to tag EC2 instances. This tests makes use of two of these tags to ensure that instances can be 
discovered and consistently referenced without us having to maintain a mapping.

- `use_case`, which for all SPs is `idp-web-tests`; we use this as a search parameter to programmatically get a list of
all instances.
- `test_ref` which must match one of the values in the `tests/models.py#ServiceProviderInstance` enum.
