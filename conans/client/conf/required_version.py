import re
import six

from conans.client.cache.cache import ClientCache
from semver import satisfies
from conans import __version__ as client_version
from conans.errors import ConanException


def validate_conan_version(required_range):
    # fix to make semver work with .post<#> version modifiers
    post_ver = re.match(r"(?P<version>.*)(\.post(?P<post>[0-9]+))$", client_version)
    local_version = post_ver.groupdict()["version"] if post_ver else client_version
    result = satisfies(local_version, required_range, loose=True, include_prerelease=True)
    if not result:
        raise ConanException("Current Conan version ({}) does not satisfy "
                             "the defined one ({}).".format(client_version, required_range))


def check_required_conan_version(cache_folder, out):
    """ Check if the required Conan version in config file matches to the current Conan version

            When required_conan_version is not configured, it's skipped
            When required_conan_version is configured, Conan's version must matches the required
            version
            When it doesn't match, an ConanException is raised

        :param cache_folder: Conan cache folder
        :param out: Output stream
        :return: None
    """
    cache = ClientCache(cache_folder, out)
    required_range = cache.config.required_conan_version
    if required_range:
        validate_conan_version(required_range)

    required_range_new = cache.new_config["core:required_conan_version"]
    if required_range_new:
        if six.PY2 and not isinstance(required_range_new, str):
            required_range_new = required_range_new.encode()
        validate_conan_version(required_range_new)
