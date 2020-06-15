import os
import configparser
from getpass import getpass
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsIntegrityError
from pykeesap.keepass_entry import KeePassEntryNew, PYKEEPASS_GROUP, SAP_ID, SAP_CLIENT

DEFAULT_SECTION = "DEFAULT"
KEE_PASS_FILE = "KeePassFile"
KEE_PASS_PASSWORD = "KeePassPassword"
KEE_PASS_KEY_FILE = "KeePassKeyFile"


class KeePassDatabase:
    kee_pass_password = None
    kee_pass_file = None
    key_file = None
    settings_file = None

    def __init__(self, settings_file=None):
        if not KeePassDatabase.settings_file and settings_file:
            KeePassDatabase.settings_file = settings_file
        self.kp = self.load_kp()

    @staticmethod
    def load_kp():
        if not KeePassDatabase.settings_file:
            print("Configuration file not set")
            return

        if not os.path.exists(KeePassDatabase.settings_file):
            print("Configuration file '{0}' not found".format(KeePassDatabase.settings_file))
            return

        config = configparser.ConfigParser()
        config.read(KeePassDatabase.settings_file)

        if DEFAULT_SECTION not in config.keys():
            print("No '{0}' in the settings.ini file".format(DEFAULT_SECTION))
            return

        if not KeePassDatabase.kee_pass_file:
            if KEE_PASS_FILE not in config[DEFAULT_SECTION].keys():
                print("No '{0}' in the settings.ini file".format(KEE_PASS_FILE))
                return
            KeePassDatabase.kee_pass_file = config[DEFAULT_SECTION][KEE_PASS_FILE]

        if not KeePassDatabase.kee_pass_password:
            if KEE_PASS_PASSWORD not in config[DEFAULT_SECTION].keys():
                print("No '{0}' in the settings.ini file".format(KEE_PASS_PASSWORD))
                return
            KeePassDatabase.kee_pass_password = config[DEFAULT_SECTION][KEE_PASS_PASSWORD]
            if KeePassDatabase.kee_pass_password is None or KeePassDatabase.kee_pass_password == "":
                KeePassDatabase.enter_password()

        if not KeePassDatabase.key_file:
            if KEE_PASS_KEY_FILE in config[DEFAULT_SECTION].keys():
                if config[DEFAULT_SECTION][KEE_PASS_KEY_FILE]:
                    KeePassDatabase.key_file = config[DEFAULT_SECTION][KEE_PASS_KEY_FILE]

        return KeePassDatabase.open_database()

    @staticmethod
    def open_database():
        try:
            if not (KeePassDatabase.kee_pass_password and KeePassDatabase.kee_pass_file):
                raise AttributeError("The KeePass Database not found")
            elif not os.path.exists(KeePassDatabase.kee_pass_file):
                raise FileNotFoundError("The KeePass Database not found")
            return PyKeePass(KeePassDatabase.kee_pass_file,
                             KeePassDatabase.kee_pass_password,
                             keyfile=KeePassDatabase.key_file)

        except (CredentialsIntegrityError, AttributeError, FileNotFoundError):
            raise RuntimeError("Couldn't open the KeePass Database file '{0}'".format(KeePassDatabase.kee_pass_file))

    def delete_entry(self, entry):
        temp_title = entry.title
        self.kp.delete_entry(entry.entry)
        self.save()
        print("The entry '{0}' deleted".format(temp_title))

    def get_entry(self, **kwargs):
        if "title" in kwargs.keys() and kwargs["title"]:
            result_entry = self.__find_entry_by_title(kwargs["title"])
        else:
            result_entry = self.__find_entry(**kwargs)
        if result_entry:
            obj = KeePassEntryNew(result_entry)
            print("The entry '{0}' found".format(obj))
            return obj

    def __find_entry_by_title(self, title):
        group = self.kp.find_groups_by_name(group_name=PYKEEPASS_GROUP, first=True)
        if not group:
            print("The group '{0}' not found".format(PYKEEPASS_GROUP))
            return

        for entry in group.entries:
            if entry.title == title:
                return entry

    def __find_entry(self, **kwargs):
        group = self.kp.find_groups_by_name(group_name=PYKEEPASS_GROUP, first=True)
        if not group:
            print("The group '{0}' not found".format(PYKEEPASS_GROUP))
            return
        if "sid" not in kwargs.keys() or not kwargs["sid"]:
            return
        sid = kwargs["sid"]
        client = kwargs["client"] if "client" in kwargs.keys() else None
        user = kwargs["user"] if "user" in kwargs.keys() else None

        max_rate = 0
        max_rate_entry = 0
        for entry in group.entries:
            rate = 0
            if sid == entry.get_custom_property(SAP_ID):
                rate += 1
            if client == entry.get_custom_property(SAP_CLIENT):
                rate += 1
            if user == entry.username:
                rate += 1

            if rate > max_rate:
                max_rate = rate
                max_rate_entry = entry

        return max_rate_entry

    @staticmethod
    def enter_password():
        KeePassDatabase.kee_pass_password = getpass('Password:')

    def create_new_entry(self, **kwargs):
        new_entry = KeePassEntryNew()
        new_entry.create_entry(self.kp, **kwargs)

    def get_all_entries(self):
        group = self.kp.find_groups_by_name(group_name=PYKEEPASS_GROUP, first=True)
        if not group:
            print("The group '{0}' not found".format(PYKEEPASS_GROUP))
            return

        for entry in group.entries:
            yield KeePassEntryNew(entry)

    def save(self):
        if self.kp is not None:
            self.kp.save()
