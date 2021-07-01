from typing import Optional, List

import click

from tests.secret_manager import SecretManager
from .models import ServiceProviderInstance, TestSecrets
from .helpers import ServiceProviderAWSOperations, load_settings, WebTestUtils
import logging

logging.basicConfig(format="%(asctime)s: %(message)s")


common_options = [
    # TODO: Fix multiple values
    click.option("--service-providers", default=None, multiple=True,
                 type=click.Choice([sp.value for sp in ServiceProviderInstance])),
    click.option('--settings-file', default='settings.yaml'),
    click.option('--settings-env', default='base'),
    click.option('--dry-run/--no-dry-run', default=False)
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def print_dry_run_disclaimer():
    click.echo("[DRY RUN MODE] No changes will be made to live resources.")


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@add_options(common_options)
def start(service_providers, settings_file, settings_env, dry_run):
    settings = load_settings(settings_file, settings_env)
    secrets = SecretManager(settings.secret_manager).get_secret_data(TestSecrets)
    if dry_run:
        print_dry_run_disclaimer()
    utils = WebTestUtils(settings, secrets)
    op = ServiceProviderAWSOperations(secrets,
                                      settings.service_provider_instance_filters,
                                      settings.aws_hosted_zone,
                                      utils)
    op.start_instances(*service_providers, dry_run=dry_run)
    op.update_instance_a_records(*service_providers, dry_run=dry_run)
    op.wait_for_ip_propagation(*service_providers, dry_run=dry_run)


@cli.command()
@add_options(common_options)
def stop(service_providers, settings_file, settings_env, dry_run):
    settings = load_settings(settings_file, settings_env)
    secrets = SecretManager(settings.secret_manager).get_secret_data(TestSecrets)
    if dry_run:
        print_dry_run_disclaimer()
    utils = WebTestUtils(settings, secrets)
    op = ServiceProviderAWSOperations(secrets,
                                      settings.service_provider_instance_filters,
                                      settings.aws_hosted_zone,
                                      utils)
    op.stop_instances(*service_providers, dry_run=dry_run)


if __name__ == "__main__":
    logging.getLogger('tests.helpers').setLevel(logging.INFO)
    cli()
