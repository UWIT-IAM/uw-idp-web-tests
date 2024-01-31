from __future__ import annotations
import logging
import sys
from contextlib import contextmanager
from typing import Dict, List, Tuple, Any, Union, Optional

import boto3
import yaml
from botocore.exceptions import ClientError
from nslookup import Nslookup
from selenium.webdriver.common.keys import Keys
from typing_extensions import Literal
from waiter import wait
from webdriver_recorder.browser import Locator, By

from .models import ServiceProviderInstance, TestSecrets, WebTestSettings, HostedZoneSettings, \
    StartInstancesRequest, StopInstancesRequest, DescribeInstancesRequest, DescribeInstancesResponse, \
    UpdateRoute53Record, AWSRoute53ChangeBatch, AWSRoute53RecordSetChange, AWSRoute53RecordSet, \
    AWSRoute53ResourceRecord, AWSEC2InstanceStateName, AWSEC2InstanceFilter, ServiceProviderConfig

logger = logging.getLogger(__name__)


def running_on_mac() -> bool:
    """When opening new tabs, we need to know whether to use CMD+T or CTRL+T; CMD+T is only valid on MacOS.
    """
    # NOTE: "darwin" here does not refer to IAM servers!
    # See: https://docs.python.org/3/library/sys.html#sys.platform
    return sys.platform == 'darwin'


CTRL_KEY = Keys.COMMAND if running_on_mac() else Keys.CONTROL


class Locators:
    """These are used to tell our test browser what DOM elements to look for. This is a convenient way to reuse
    elements across tests without having to redeclare them.
    """
    submit_button = Locator(search_method=By.ID, search_value='submit_button')
    logout_button = Locator(search_method=By.CSS_SELECTOR, search_value='input[value="Logout"]')
    iframe = Locator(search_method=By.ID, search_value='duo_iframe')
    passcode_button = Locator(search_method=By.ID, search_value='passcode')


def lookup_domain_ip(domain: str):
    """Given a domain, returns its A record value."""
    response = Nslookup().dns_lookup(domain).response_full
    a_record_responses = list(filter(lambda r: ' IN A ' in r, response))
    if not a_record_responses:
        return None
    return a_record_responses[0].split()[-1]


def load_settings(filename: str, env: str,
                  option_overrides: Optional[Dict[str, Any]] = None, **kwargs) -> WebTestSettings:
    """Given the file name and the profile name, loads the YAML and returns the settings model."""
    option_overrides = option_overrides or {}
    kwargs = {k: v for k,v in kwargs.items() if v is not None}
    with open(filename) as f:
        data = yaml.load(f, yaml.SafeLoader)[env]
    data.update(kwargs)
    settings = WebTestSettings.parse_obj(data)
    settings.test_options = settings.test_options.copy(update=option_overrides)
    return settings


def validate_dry_run(error: ClientError):
    """AWS client error handling is confusing at best, and relies on nested attributes to figure out what ACTUALLY
    happened. This wone tells us if an error was a DryRunOperation error (which is not an error at all!).
    """
    return error.response['Error']['Code'] == 'DryRunOperation'


@contextmanager
def dry_runnable_operation(dry_run=False):
    """
    AWS dry run operations throw a special error if the dry run was successful. (::eyeroll::)
    Use:
        with dry_runnable_operation(True):
            aws_client.do_work(...)
    """
    try:
        yield
    except ClientError as e:
        if dry_run and validate_dry_run(e):
            return
        raise


class ServiceProviderAWSOperations:
    """Various functions to start and stop AWS EC2 instances."""
    def __init__(self,
                 test_secrets: TestSecrets,
                 service_provider_instance_filters: List[AWSEC2InstanceFilter],
                 hosted_zone_settings: HostedZoneSettings, utils: WebTestUtils):
        self._clients = {}
        self._sp_instance_filters = service_provider_instance_filters
        self._zone_settings = hosted_zone_settings
        self._utils = utils
        self._secrets = test_secrets.env
        self.service_providers = self._build_sp_configs()

    def _get_lazy_cache_client(self, client: Literal['ec2', 'route53']):
        if client not in self._clients:
            self._clients[client] = boto3.client(
                client,
                aws_access_key_id=self._secrets['AWS_ACCESS_KEY_ID'].get_secret_value(),
                aws_secret_access_key=self._secrets['AWS_SECRET_ACCESS_KEY'].get_secret_value()
            )
        return self._clients[client]

    def _build_sp_configs(self) -> Dict[ServiceProviderInstance, ServiceProviderConfig]:
        query = DescribeInstancesRequest(filters=self._sp_instance_filters)
        response = DescribeInstancesResponse.parse_obj(self.ec2_client.describe_instances(**query.request_payload))
        sp_configs = {}
        for reservation in response.reservations:
            for instance in reservation.instances:
                config = ServiceProviderConfig(
                    instance_id=instance.instance_id,
                    domain_suffix=self._zone_settings.name,
                    ref=instance.get_tag('test_ref'),
                    public_ip=instance.public_ip_address,
                    last_known_state=instance.state.name
                )
                sp_configs[ServiceProviderInstance(config.ref)] = config
        return sp_configs

    def _get_record_sets(self):
        client = self._get_lazy_cache_client('route53')
        record_sets = client.list_resource_record_sets(
            HostedZoneId=self._zone_settings.id,
        )
        record_sets = record_sets['ResourceRecordSets']
        return record_sets

    @property
    def record_sets(self) -> List[Dict]:
        return self._get_record_sets()

    def dns_record_requires_update(self, record_sets, service_provider):
        sp = self.service_providers[service_provider]
        domain = self._utils.service_provider_domain(service_provider)

        for record in record_sets:
            record_domain = record['Name'][:-1]  # Records include a trailing '.'
            if record_domain == domain and record['Type'] == 'A':
                return record['ResourceRecords'][0]['Value'] != sp.public_ip
        return True

    @property
    def ec2_client(self):
        return self._get_lazy_cache_client('ec2')

    @property
    def route53_client(self):
        return self._get_lazy_cache_client('route53')

    def start_instances(self, *service_providers: ServiceProviderInstance, dry_run=False):
        """
        Starts the instances provided (or all of them, if none are provided).
        If dry_run=true, will only validate the call, and not actually
        change anything. This is a blocking function that will not return until the given instances are running
        (or until the AWS-vended waiter times out).

        Note that this does _not_ change DNS settings, only starts the instances. See "update_instance_a_record()."
        """
        service_providers = service_providers or tuple([
            sp for sp in self.service_providers.keys() if not self.instance_is_started(sp)
        ])
        if not service_providers:
            logger.info("All instances are already running. Nothing to do!")
            return
        instance_ids = self._get_instance_ids(service_providers)
        instance_descriptors = [
            f'{service_providers[index]} ({instance})'
            for index, instance in enumerate(instance_ids)
        ]
        instance_descriptors = ', '.join(instance_descriptors)
        logger.info(f"Requesting start of instances: {instance_descriptors}")
        with dry_runnable_operation(dry_run):
            self.ec2_client.start_instances(
                **StartInstancesRequest(instance_ids=instance_ids, dry_run=dry_run).dict(by_alias=True))

        logger.info("Waiting for instances to become active.")
        if not dry_run:
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=instance_ids)

        self.service_providers = self._build_sp_configs()
        logger.info("All requested instances have started.")

    def stop_instances(self, *service_providers: ServiceProviderInstance, dry_run=False):
        """
        Stops the instances provided (or all of them, if none are provided). If dry_run=True, will only
        validate the call, and not actually change anything. this is a blocking function that will not return until
        the given instances are stopped (or until the AWS-vended waiter times out).
        """
        service_providers = service_providers or tuple(self.service_providers.keys())
        instance_ids = self._get_instance_ids(service_providers)
        logger.info(f"Requesting stop of instances: {instance_ids}")

        with dry_runnable_operation(dry_run):
            self.ec2_client.stop_instances(
                **StopInstancesRequest(instance_ids=instance_ids, dry_run=dry_run).dict(by_alias=True))

        logger.info("Waiting for instances to shut down.")
        if not dry_run:
            waiter = self.ec2_client.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=instance_ids)

        self.service_providers = self._build_sp_configs()
        logger.info("All requested instances have stopped.")

    def _get_instance_ids(self, service_providers: Tuple[ServiceProviderInstance]):
        return [self.service_providers[sp].instance_id for sp in service_providers]

    def update_instance_a_records(self, *service_providers: ServiceProviderInstance, dry_run: bool = False):
        """
        When starting instances, there is no guarantee it will have the same IP address as it had before; this will
        update DNS records for the test service providers and wait for those new IPs to be resolvable before
        returning.

        If dry_run is true, the changes will be calculated and the payload created, but no call will be submitted
        to AWS (AWS Route53 does not support dry runs like EC2 does).

        NB: It may be that this also waits for the changes to have propagated, but if so, is not documented. This call
        sometimes takes a few minutes, but it is unknown whether this is the reason why.
        """
        service_providers = service_providers or tuple(self.service_providers.keys())

        changes = [
            AWSRoute53RecordSetChange(resource_record_set=AWSRoute53RecordSet(
                name=self.service_providers[sp].domain,
                ttl=60,
                resource_records=[AWSRoute53ResourceRecord(value=self.service_providers[sp].public_ip)]
            ))
            for sp in service_providers
        ]

        for change in changes:
            logger.info(f"Updating {change.resource_record_set.name} A record "
                        f"to {change.resource_record_set.resource_records[0].value}")

        if dry_run or not changes:
            return

        request = UpdateRoute53Record(
            hosted_zone_id=self._zone_settings.id,
            change_batch=AWSRoute53ChangeBatch(changes=changes),
        )
        response = self.route53_client.change_resource_record_sets(**request.request_payload)
        request_id = response['ChangeInfo']['Id']
        logger.info("Waiting for DNS configuration to complete.")
        waiter = self.route53_client.get_waiter('resource_record_sets_changed')
        waiter.wait(Id=request_id)

    def wait_for_ip_propagation(self, *service_providers: ServiceProviderInstance, dry_run=False):
        """
        Ensures that, for each service provider given (or all of them, if none are given), the SP
        resolves to the IP address assigned by AWS. This waits for as long as the TTL setting in settings.yaml says it
        should, plus 10% longer to account for any timing jitter. If the domain still doesn't resolve the provided IP
        address, an error will be raised.
        """
        service_providers = service_providers or tuple(self.service_providers.keys())
        logger.info("Waiting for test service provider DNS settings to propagate")
        # A TTL of 300 will check every 30 seconds
        wait_seconds = (self._zone_settings.ttl / 10)
        # We add wait_seconds to our TTL to account for edge cases with polling and TTL cycles.
        wait_timeout = self._zone_settings.ttl + wait_seconds
        for sp in service_providers:
            waiter = wait(wait_seconds, wait_timeout)
            # This winds up as something like diafine6.sandbox.iam.s.uw.edu
            domain = self.service_providers[sp].domain
            desired_ip = self.service_providers[sp].public_ip
            logger.info(f"Waiting for {domain} ({desired_ip})")
            if dry_run:
                continue
            try:
                waiter.poll(lambda ip: ip == desired_ip, lookup_domain_ip, domain)
            except StopIteration:
                raise TimeoutError(f"IP address for {domain} never updated to {desired_ip}")
        logger.info("All requested changes have propagated.")

    def instance_is_started(self, sp: ServiceProviderInstance):
        return self.service_providers[sp].last_known_state == AWSEC2InstanceStateName.RUNNING

    def instance_is_stopped(self, sp: ServiceProviderInstance):
        return self.service_providers[sp].last_known_state == AWSEC2InstanceStateName.STOPPED


class WebTestUtils:
    """Pytest fixtures are great, but better for object instances than functions. If you want to write a function
    that requires other fixtures, this is the best place to do it.

    This is set as the return value of the `utils` fixture, and thus every one of its functions can be
    accessed at runtime:

    ```
    def test_my_thing(utils):
        utils.do_work()
    ```
    """
    def __init__(self, settings: WebTestSettings, secrets: TestSecrets):
        self._settings = settings
        self._secrets = secrets
        self._sp_aws_ops = None

    @property
    def sp_aws_operations(self) -> ServiceProviderAWSOperations:
        if not self._sp_aws_ops:
            self._sp_aws_ops = ServiceProviderAWSOperations(
                self._secrets,
                self._settings.service_provider_instance_filters,
                self._settings.aws_hosted_zone,
                self)
        return self._sp_aws_ops

    @property
    def settings(self):
        return self._settings

    @contextmanager
    def using_test_sp(self, *service_providers: ServiceProviderInstance):
        """
        Ensures that the test service_providers is turned on before the test executes.
        :param service_providers:
        :return:
        """
        need_to_start = [sp for sp in service_providers if not self.sp_aws_operations.instance_is_started(sp)]
        if need_to_start:
            self.sp_aws_operations.start_instances(*need_to_start)
            self.sp_aws_operations.update_instance_a_records(*need_to_start)
        yield

    def service_provider_domain(self, service_provider: ServiceProviderInstance) -> str:
        return f'{service_provider.value}.{self._settings.aws_hosted_zone.name}'

    def service_provider_url(self, service_provider: ServiceProviderInstance) -> str:
        return f'https://{self.service_provider_domain(service_provider)}'
