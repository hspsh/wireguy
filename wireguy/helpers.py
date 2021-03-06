import logging
from functools import wraps

from flask import request, abort
from wireguy.settings import ip_mask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#TODO(critbit): these shouldn't be needed after removing whois specific parts
def owners_from_devices(devices):
    return set(filter(None, map(lambda d: d.owner, devices)))


def filter_hidden(entities):
    return list(filter(lambda e: not e.is_hidden, entities))


def filter_anon_names(users):
    return list(filter(lambda u: not u.is_name_anonymous, users))


def unclaimed_devices(devices):
    return list(filter(lambda d: d.owner is None, devices))


def ip_range(mask, address):
    """
    Checks if given address is in space defined by mask
    :param mask: string for ex. '192.168.88.1-255'
    :param address:
    :return: boolean
    """
    ip_parts = address.split(".")
    for index, current_range in enumerate(mask.split(".")):
        if "-" in current_range:
            mini, maxi = map(int, current_range.split("-"))
        else:
            mini = maxi = int(current_range)
        if not (mini <= int(ip_parts[index]) <= maxi):
            return False
    return True

#TODO(critbit): note this as example how to add your own decorators
def in_space_required():
    def decorator(f):
        @wraps(f)
        def func(*a, **kw):
            if request.headers.getlist("X-Forwarded-For"):
                ip_addr = request.headers.getlist("X-Forwarded-For")[0]
                logger.info(
                    "forward from %s to %s",
                    request.remote_addr,
                    request.headers.getlist("X-Forwarded-For")[0],
                )
            else:
                ip_addr = request.remote_addr

            if not ip_range(ip_mask, ip_addr):
                logger.error("{} request from outside".format(ip_addr))
                abort(403)
            else:
                logger.info("{} is in allowed ip range".format(ip_addr))
                return f(*a, **kw)

        return func

    return decorator
