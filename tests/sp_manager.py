from typing import Optional, List

import click
from .models import ServiceProviderInstance, WebTestSettings
from .helpers import ServiceProviderAWSOperations, load_settings, WebTestUtils
import logging
import os

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
    if dry_run:
        print_dry_run_disclaimer()
    utils = WebTestUtils(settings)
    op = ServiceProviderAWSOperations(settings.service_providers, settings.aws_hosted_zone, utils)
    op.start_instances(*service_providers, dry_run=dry_run)
    op.update_instance_a_records(*service_providers, dry_run=dry_run)
    op.wait_for_ip_propagation(*service_providers, dry_run=dry_run)


@cli.command()
@add_options(common_options)
def stop(service_providers, settings_file, settings_env, dry_run):
    settings = load_settings(settings_file, settings_env)
    if dry_run:
        print_dry_run_disclaimer()
    utils = WebTestUtils(settings)
    op = ServiceProviderAWSOperations(settings.service_providers, settings.aws_hosted_zone, utils)
    op.stop_instances(*service_providers, dry_run=dry_run)


if __name__ == "__main__":
    logging.getLogger('tests.helpers').setLevel(logging.INFO)
    cli()
