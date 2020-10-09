from __future__ import annotations

import os
from typing import Type, Optional
from typing import TypeVar

import click
from google.cloud import secretmanager
from google.cloud.secretmanager_v1 import AddSecretVersionRequest, SecretPayload
from pydantic import BaseModel

from tests.helpers import load_settings
from tests.models import SecretManagerSettings

SecretModelType = TypeVar('SecretModelType', bound=BaseModel)


class SecretManager:
    def __init__(self, settings: SecretManagerSettings):
        self._settings = settings
        self._secrets = None
        self._client = None

    @property
    def client(self) -> secretmanager.SecretManagerServiceClient:
        if not self._client:
            self._client = secretmanager.SecretManagerServiceClient()
        return self._client

    def publish_new_version(self, data: bytes):
        request = AddSecretVersionRequest(
            parent=self._settings.canonical_name,
            payload=SecretPayload(data=data)
        )
        return self.client.add_secret_version(request=request)

    def get_secret_data(self, model_type: Optional[Type[SecretModelType]] = None) -> SecretModelType:
        response = self.client.access_secret_version(name=self._settings.canonical_version_name)
        data = response.payload.data.decode('UTF-8')
        if model_type is None:
            return data
        return model_type.parse_raw(data)


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.option('--settings-file', default='settings.yaml')
@click.option('--settings-profile', default='base')
@click.option('--filename', '-f', required=True)
def publish(filename: str, settings_file: str, settings_profile: str):
    service = SecretManager(load_settings(settings_file, settings_profile).secret_manager)
    with open(filename, 'rb') as f:
        response = service.publish_new_version(f.read())
        click.echo(f"Successfully published {response.name} from {filename}")
        delete_local = click.confirm("Would you like to remove the source file from your system?")
        if delete_local:
            os.remove(filename)
            click.echo(f"Deleted {filename}")


@cli.command()
@click.option('--settings-file', default='settings.yaml')
@click.option('--settings-profile', default='base')
@click.option('--filename', '-f', default='secrets.json')
def download(settings_file, settings_profile, filename):
    service = SecretManager(load_settings(settings_file, settings_profile).secret_manager)
    data = service.get_secret_data()
    with open(filename, 'w') as f:
        f.write(data)
    click.echo(f"Successfully downloaded secrets to {filename}")


if __name__ == "__main__":
    cli()
