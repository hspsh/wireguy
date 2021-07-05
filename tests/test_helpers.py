from wireguy.helpers import *


class UserDummy:
    def __init__(self, id, username, display_name):
        self.id = id
        self.username = username
        self.display_name = display_name
        self.is_name_anonymous = True
        self.is_hidden = False

'''
class DeviceDummy:
    def __init__(self, mac, owner, hidden):
        self.mac_address = mac
        self.owner = owner
        self.is_hidden = hidden


user_fixtures = [[1, "user12", "user man"], [2, "admin", "system administratot"]]
users = list(map(lambda f: UserDummy(*f), user_fixtures))
device_fixtures = [
    ["aa:aa:aa:aa:aa:aa", None, False],
    ["00:00:00:00:00:00", users[1], True],
]
devices = list(map(lambda f: DeviceDummy(*f), device_fixtures))

'''