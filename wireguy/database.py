import os
from datetime import datetime, timedelta

import peewee as pw
from werkzeug.security import check_password_hash, generate_password_hash
from wireguy.settings import DB_PATH

db = pw.SqliteDatabase(DB_PATH)

#TODO(critbit): propably remove
class User(pw.Model):
    id = pw.UUIDField(primary_key=True)
    username = pw.CharField(unique=True)

    #flags = pw.BitField(null=True)

    class Meta:
        database = db

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True

#TODO(critbit) you could rewrite this, ad owner_id as uuid, to match this in keycloak
class Peer(pw.Model):
    #id = pw.PrimaryKeyField()
    user = pw.ForeignKeyField(
        User, backref="peers", column_name="user_id", null=True
    )

    pubkey = pw.CharField()
    ip =  pw.CharField()
    
    mac_address = pw.FixedCharField(primary_key=True, unique=True, max_length=17)
    hostname = pw.CharField(null=True)
    last_seen = pw.DateTimeField()
    comment = pw.CharField()

    #flags = pw.BitField(null=True)

    class Meta:
        database = db

    def __str__(self):
        return self.mac_address
    '''
    @classmethod
    def update_or_create(cls, mac_address, last_seen, hostname=None):
        try:
            res = cls.create(
                mac_address=mac_address, hostname=hostname, last_seen=last_seen
            )

        except pw.IntegrityError:
            res = cls.get(cls.mac_address == mac_address)
            res.last_seen = last_seen
            res.hostname = hostname

        res.save()
    '''