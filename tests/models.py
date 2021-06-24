from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field, Extra, BaseSettings, validator
import inflection


# Enums


# Converts the values from AWS into a meaningful symbol, so we don't have to look up possible values from
# AWS all the time.
class AWSEC2InstanceStateName(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SHUTTING_DOWN = 'shutting-down'
    TERMINATED = 'terminated'
    STOPPING = 'stopping'
    STOPPED = 'stopped'


# Helps us avoid silly typos by converting these into symbols
# In order to resolve to an instance, the instance must have a `test_ref` tag equivalent to the declared value here.
# See docs/test-service-providers.md
class ServiceProviderInstance(Enum):
    diafine6 = 'diafine6'
    diafine7 = 'diafine7'
    diafine8 = 'diafine8'
    diafine9 = 'diafine9'
    diafine10 = 'diafine10'
    diafine11 = 'diafine11'
    diafine12 = 'diafine12'


# Helps us avoid silly typos by converting these into symbols
class AccountNetid(Enum):
    sptest01 = 'sptest01'
    sptest02 = 'sptest02'
    sptest03 = 'sptest03'
    sptest04 = 'sptest04'
    sptest05 = 'sptest05'
    sptest06 = 'sptest06'
    sptest07 = 'sptest07'
    sptest08 = 'sptest08'
    sptest10 = 'sptest10'


# Test Suite Models


class ServiceProviderConfig(BaseModel):
    """Used to track a test SPs known state."""
    ref: str
    domain_suffix: str
    instance_id: str
    public_ip: Optional[str]
    last_known_state: Optional[AWSEC2InstanceStateName]

    @property
    def domain(self):
        """convenience property to extract a canonical domain for the test SP."""
        return f'{self.ref}.{self.domain_suffix}'

    @property
    def url(self):
        """Convenience property to extract a canonical URL for the test SP."""
        return f'https://{self.domain}'


class HostedZoneSettings(BaseModel):
    name: str  # Used to build URLs
    id: str  # Must be retrieved from AWS Route53 for the zone matching the name above
    ttl: int  # Only used as a waiter sentinel; does not affect actual DNS TTL!


class SecretManagerSettings(BaseModel):
    project: str
    secret_name: str
    version: str

    @property
    def canonical_name(self) -> str:
        return f'projects/{self.project}/secrets/{self.secret_name}'

    @property
    def canonical_version_name(self) -> str:
        return f'{self.canonical_name}/versions/{self.version}'


class TestAccountSecrets(BaseModel):
    password: str
    duo_code: str = Field(..., alias='duoCode')


class TestSecrets(BaseModel):
    env: Dict[str, str]
    test_accounts: TestAccountSecrets = Field(..., alias='testAccounts')


class TestOptions(BaseSettings):
    skip_test_service_provider_start: bool = Field(
        ..., description="If set to true, will only start test SPs if they are needed.")
    skip_test_service_provider_stop: bool = Field(
        ..., description="If set to true, will not shut down instances at the end of the test.")
    hosts_file: str = Field(..., description="The location of the hosts file on this system.")
    use_local_secrets: bool = Field(
        False, description="If set to True will use local_secrets_filename instead of the default")
    local_secrets_filename: Optional[str] = Field(
        None, description="If provided along with --use-local-secrets, "
                          "will use this file for secrets instead of retrieving them from GCP")
    report_title: Optional[str] = Field(
        'UW IdP Web Tests',
        add_cli_arg=False,
        description='The title of the report artifact.',
    )
    selenium_server: Optional[str] = Field(
        None,
        add_cli_arg=False,
        description='If provided will use a Remote instance connection to the server.'
    )

    @classmethod
    def parse_overrides(cls, test_config):
        """"""
        kwargs = {}
        for field, f_config in cls.__fields__.items():
            option_name = f'--{inflection.dasherize(field)}'
            option_value = test_config.getoption(option_name)
            if option_value is not None:
                kwargs[field] = option_value
        return kwargs

    @validator('local_secrets_filename')
    def validate_filename_if_using_local_secrets(cls, v, values):
        if values.get('use_local_secrets') and not v:
            raise ValueError("use_local_secrets is on, but no local filename was provided.")
        return v


class WebTestSettings(BaseSettings):
    """See settings.yaml for documentation on these settings"""
    class Config:
        use_enum_values = True

    service_provider_instance_filters: List[AWSEC2InstanceFilter]
    aws_hosted_zone: HostedZoneSettings
    secret_manager: SecretManagerSettings
    test_options: TestOptions


################
# AWS Models -- These map to boto3 API requests and responses,
# but only contain fields we're actually interested in. See the README for links to
# AWS documentation if you need to update or expand these models.
#
# When using these for request submissions, pass only them in as splatted dictionaries:
#   aws_client.some_request(**some_model.dict(by_alias=True))
#
# When building these from responses, use parse_obj:
#   response = ResponseModel.parse_obj(aws_client.some_request(...))
################


def camelize_aws(value: str) -> str:
    return inflection.camelize(value, uppercase_first_letter=True)


class AWSBaseModel(BaseModel):
    class Config:
        # Allows pythonic as well as CamelCase initialization of fields
        allow_population_by_field_name = True
        # Ignores any fields in the base payload that aren't mapped in the model;
        # this allows us to "opt in" to fields as needed.
        extra = Extra.ignore
        # This automatically sets a CamelCase alias per AWS standard; can still
        # be overridden by the alias Field parameter.
        alias_generator = camelize_aws

    @property
    def request_payload(self):
        return self.dict(by_alias=True, exclude_none=True)



class AWSEC2InstanceTag(AWSBaseModel):
    key: str
    value: str


class StartInstancesRequest(AWSBaseModel):
    instance_ids: List[str]
    dry_run: bool = False


class StopInstancesRequest(StartInstancesRequest):
    hibernate: bool = False
    force: bool = False


class AWSEC2InstanceState(AWSBaseModel):
    name: AWSEC2InstanceStateName


class AWSEC2InstanceLifecycleResponse(AWSBaseModel):
    current_state: AWSEC2InstanceState
    instance_id: str
    previous_state: AWSEC2InstanceState


class StartInstancesResponse(AWSBaseModel):
    starting_instances: List[AWSEC2InstanceLifecycleResponse]


class StopInstancesResponse(AWSBaseModel):
    stopping_instances: List[AWSEC2InstanceLifecycleResponse]


class AWSEC2InstanceFilter(AWSBaseModel):
    # For more information about allowed filters and how they are used,
    # see the AWS EC2 Boto3 documentation linked from the README.
    name: str
    values: List[Any] = []


# Needed here because we define WebTestSettings before AWSEC2InstanceFilter.
WebTestSettings.update_forward_refs()


class DescribeInstancesRequest(AWSBaseModel):
    instance_ids: Optional[List[str]]
    dry_run: bool = False
    filters: Optional[List[AWSEC2InstanceFilter]]


class DescribeInstancesResponseInstance(AWSBaseModel):
    instance_id: str
    public_ip_address: Optional[str]  # AWS does not include this if the instance is turned off.
    state: AWSEC2InstanceState
    tags: List[AWSEC2InstanceTag] = []

    def get_tag(self, tag_name) -> Optional[str]:
        for t in self.tags:
            if t.key == tag_name:
                return t.value
        return None


class DescribeInstanceResponseReservation(AWSBaseModel):
    instances: List[DescribeInstancesResponseInstance] = []


class DescribeInstancesResponse(AWSBaseModel):
    reservations: List[DescribeInstanceResponseReservation] = []


class AWSRoute53ResourceRecord(AWSBaseModel):
    value: str


class AWSRoute53RecordSet(AWSBaseModel):
    name: str
    # We currently only modify A records. If we ever need to support more
    # record types for these web tests, should factor the supported types to an Enum,
    # as with AWSEC2InstanceStateName
    type: str = Field('A', const=True)
    ttl: int = Field(300, alias='TTL')
    resource_records: List[AWSRoute53ResourceRecord] = []


class AWSRoute53RecordSetChange(AWSBaseModel):
    # We currently only use upsert operations; if ever we need to support creation
    # or deletion, we should factor the actions to an Enum, as with AWSEC2InstanceStateName
    action: str = Field('UPSERT', const=True)
    resource_record_set: AWSRoute53RecordSet


class AWSRoute53ChangeBatch(AWSBaseModel):
    changes: List[AWSRoute53RecordSetChange]


class UpdateRoute53Record(AWSBaseModel):
    hosted_zone_id: str
    change_batch: AWSRoute53ChangeBatch
