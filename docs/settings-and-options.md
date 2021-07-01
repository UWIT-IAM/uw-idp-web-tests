# Test Settings and Options

This test suite aims to be highly configurable where needed. Because there are lots of moving parts here, all 
settings can be loaded from a `.yaml` file. 

By default, the tests will use the included `settings.yaml` with the `base` "profile."  

Included in the yaml is a section called `test_options`; these are special settings that also correlate to 
command line arguments, so that you don't have to always express overrides in yaml. 

The order of precedence becomes: 

- (lowest priority) Modeled defaults (`tests/models.py#WebTestSettings`) where provided
- Declarative YAML (`settings.yaml`)
- (highest priority) Command-line overrides

To that end, it's important to remember that "settings" can only be controlled via yaml, but "options" can be 
toggled at the command line.

## Running against prod or eval

The tests can be run against the production environment or the test/eval environment
To run the tests against production use the command line argument `--env=prod`
To run the tests against eval use the command line argument `--env=eval`
If you do not use the `--env` flag, the tests will run against production as default.

## Switching profiles

If you want to run tests using a different set of settings, you can override this two ways.

One is by using the `--settings-file` flag, which allows you to provide an alternative file to `settings.yaml`. This
needs to be a file that defines the complete structure of the settings. It should be provided as an absolute path.

`pytest --settings-file /path/to/my/settings.yaml`

Alternatively, you can change which profile to use within the settings file. Each profile is a root note in the yaml.

For instance, if wanted to create a permanent profile for some special case that uses a different AWS hosted zone 
for the test SPs, you can override those settings like so:

```yaml
special_case: *base  # Inherit all entries from the base profile
  aws_hosted_zone:  # But override this particular section
    name: altzone.iam.s.uw.edu
    id: f00bar
    ttl: 300
```

And then use this profile with: `pytest --settings-profile special_case`

## Adding new settings

### Updating the settings model

**To add a new setting, you must first add it to the corresponding model** (`WebTestSettings` in `tests/models.py`). Each 
"section" of the settings needs its own submodel (e.g., `SecretManagerSettings` in `tests/models.py`. So, if you want to
add a setting to an existing model, simply declare it:

* `some_new_setting: SettingType  # No default`  
* `some_new_setting: Optional[SettingType] # default to None` -- only use this if you _actually_ 
expect it to be None sometimes, and if that value is meaningful in some way 
* `some_new_setting: SettingType = SettingType(some_value="some_default")  # Default value if none is provided`

For consistency and maintainability it is to _not_ set defaults on atomic items (string, int, bool), but to set 
empty defaults of iterables (List, Dict)):

```python
port: int
hosts: List[str] = []
```

This way, nobody has to do a null-check for collections, so things like `for x in hosts` will always work, even if 
none were provided. 

Otherwise, it's better to require an option, rather than set a default in the model AND in the default settings.yaml; 
otherwise, we have to remember to update both if one changes. 

For more information, see [Pydantic documentation](https://pydantic-docs.helpmanual.io/)

### Add the desired default to settings.yaml

If appropriate, also add the setting to `settings.yaml`; this file should exactly match the model's mapping. 

```yaml
base:
  port: 5555
  hosts: 
    - foo1
    - foo2
```

## Adding new options

Adding new _options_ is similar to the above, except they cannot be nested. You must add them to the `TestOptions` 
model in `tests/models.py`. If an option is meant as a boolean flag, you must provide a default, so that the
test suite can determine how to interpret the flag itself.

In other words, the default to boolean flags must represent the state if the flag is _not_ used. 

```python
class TestOptions(BaseSettings):
    # . . .
    skip_some_step: bool = False
```

This would allow a user to include the flag `--skip-some-step` from the command line, which would set the value of 
that option to `True`.

If we have a test configuration that will always want to skip "some step," we can override this in the settings like so:

```yaml
test_options:
 skip_some_step: True
```

The test suite automatically adds test options to available CLI args; you can view a list of those args with

```bash
pytest --help
```

And look for the "custom options" section.


## Declaring help text to settings and options

If you want to add help text to your settings, you can declare them as part of the model field's `description`, which 
requires importing the `Field` object from pydantic. Note that if you do not want to provide a default, you can use the 
`...` "keyword" in place of the required default argument:

```
from pydantic import Field 

class TestOptions(BaseSettings):
    # . . . 
    skip_some_step: bool = Field(False, description="Here is some help text about this option.")

class SecretManagerSettings(BaseSettings):
    # . . .
    some_new_field: str = Field(..., description="Here is some help text about this required parameter.")
```

Yes, `...` is actual code, and is not just a placeholder for you to figure out on your own.
