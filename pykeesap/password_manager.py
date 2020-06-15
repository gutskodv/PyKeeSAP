import re
import os
import configparser
import pykeesap
from pykeesap.keepass_base import KeePassDatabase, DEFAULT_SECTION
from pysapgui.sapnewsession import SAPNewSession
from pysapgui.saplogonini import SAPLogonINI
from pysapgui.saplogonexe import SAPLogonEXE
from pysapgui.sapexistedsession import SAPExistedSession
from pysapgui.saplogonpwd import SAPLogonPwd

PASSWORD_POLICY = "PASSWORD POLICY"
SAPLOGON_EXE_PATH = "SaplogonEXE"

GLOBAL_INI = "GlobalSaplogonINI"
LOCAL_INI = "LocalSaplogonINI"


class SAPPasswordManager:
    @staticmethod
    def __open_kp():
        try:
            path = os.path.join(os.path.dirname(pykeesap.__file__), pykeesap.SETTINGS_FILE)
            kp = KeePassDatabase(path)
        except RuntimeError as error:
            print(str(error))
        else:
            return kp

    @staticmethod
    def __try_to_connect(kp, entry, close_conn=True):
        SAPLogonINI.set_ini_files(*SAPPasswordManager.__get_ini_files())
        SAPLogonPwd.set_password_policy(SAPPasswordManager.__get_password_policy())
        SAPLogonEXE.set_path(SAPPasswordManager.__get_saplogonexe_path())

        print("Trying to connect to '{0}' (user: '{1}')".format(entry.sid, entry))
        try:
            saplogon = SAPLogonEXE.start()
            if not saplogon:
                raise RuntimeError("SAP Logon Application not found. Couldn't start SAP Logon")
            result = SAPNewSession.create_new_session(entry.sid, entry.username, entry.password, client=entry.client,
                                                      langu=entry.langu, close_conn=close_conn)
        except (RuntimeError, ValueError) as error:
            print(str(error))
            return
        else:
            print("Successfully connected to '{0}'".format(entry.sid, entry.username))
            if result is not None:
                print("Password changed (user '{0}')".format(entry.user))
                entry.change_password(kp, result)

    @staticmethod
    def __get_ini_files():
        config = configparser.ConfigParser()
        path = os.path.join(os.path.dirname(pykeesap.__file__), pykeesap.SETTINGS_FILE)
        config.read(path)

        global_ini = config[DEFAULT_SECTION][GLOBAL_INI]
        local_ini = config[DEFAULT_SECTION][LOCAL_INI]

        return global_ini, local_ini

    @staticmethod
    def __get_password_policy():
        config = configparser.ConfigParser()
        path = os.path.join(os.path.dirname(pykeesap.__file__), pykeesap.SETTINGS_FILE)
        config.read(path)

        if PASSWORD_POLICY in config.keys():
            return config._sections[PASSWORD_POLICY]

    @staticmethod
    def __get_saplogonexe_path():
        config = configparser.ConfigParser()
        path = os.path.join(os.path.dirname(pykeesap.__file__), pykeesap.SETTINGS_FILE)
        config.read(path)

        if SAPLOGON_EXE_PATH in config[DEFAULT_SECTION].keys():
            return config[DEFAULT_SECTION][SAPLOGON_EXE_PATH]

    @staticmethod
    def __check_sid(sid):
        if re.match(r"^[A-Z0-9]{3}$", sid):
            return True

        print("Bad SAP ID '{0}'".format(sid))
        return False

    @staticmethod
    def __check_client(client, is_none=True):
        if client is None:
            return is_none

        if re.match(r"^[0-9]{3}$", client):
            return True

        print("Bad SAP Client '{0}'".format(client))
        return False

    @staticmethod
    def __check_user(user, is_none=True):
        if len(user) <= 12:
            return is_none

        print("Bad SAP User '{0}'".format(user))
        return False

    @staticmethod
    def __change_system_password(kp, entry):
        if kp and entry:
            sap_session = None
            new_pwd = None
            try:
                SAPPasswordManager.__try_to_connect(kp, entry, close_conn=False)
                session_count = SAPExistedSession.get_session_count()
                sap_session = SAPExistedSession.get_session_by_number(session_count - 1)
                new_pwd = SAPLogonPwd.change_password_su3(sap_session, entry.password)
                SAPExistedSession.close_session(sap_session)
            except (AttributeError, PermissionError, RuntimeError) as error:
                print(str(error))
            else:
                if new_pwd:
                    entry.change_password(kp, new_pwd)
                    print('Password changed')
            finally:
                if sap_session:
                    SAPExistedSession.close_session(sap_session)

    @staticmethod
    def change_keepass_password(args):
        kp = SAPPasswordManager.__open_kp()
        if not kp:
            return

        entry = kp.get_entry(**vars(args))
        if entry:
            entry.change_password(kp, args.pwd)

    @staticmethod
    def delete_entry(args):
        kp = SAPPasswordManager.__open_kp()
        if kp:
            entry = kp.get_entry(**vars(args))
            if entry:
                kp.delete_entry(entry)
            else:
                print("The entry '{title}' not found".format(**vars(args)))

    @staticmethod
    def print_users(args):
        kp = SAPPasswordManager.__open_kp()
        if not kp:
            return

        print('The KeePass Database entries:')
        no_entries = True
        for entry in kp.get_all_entries():
            if not args.sid or args.sid == entry.sid:
                no_entries = False
                print(entry)
        if no_entries:
            print('No entries')

    @staticmethod
    def change_system_password(args):
        kp = SAPPasswordManager.__open_kp()
        if not kp:
            return

        entry = kp.get_entry(**vars(args))
        if entry:
            SAPPasswordManager.__change_system_password(kp, entry)

    @staticmethod
    def multi_change_password(args):
        kp = SAPPasswordManager.__open_kp()
        if not kp:
            return

        for entry in kp.get_all_entries():
            SAPPasswordManager.__change_system_password(kp, entry)

    @staticmethod
    def create_entry(args):
        if not (SAPPasswordManager.__check_sid(args.sid) and
                SAPPasswordManager.__check_client(args.client) and
                SAPPasswordManager.__check_user(args.user)):
            return

        kp = SAPPasswordManager.__open_kp()
        if kp:
            kp.create_new_entry(**vars(args))

    @staticmethod
    def login(args):
        if not (SAPPasswordManager.__check_sid(args.sid) and SAPPasswordManager.__check_client(args.client)):
            return

        kp = SAPPasswordManager.__open_kp()
        if not kp:
            return

        entry = kp.get_entry(**vars(args))
        if not entry:
            if args.client:
                print("Entries not found for system '{0}', client '{1}' in the KeePass Database".format(args.sid,
                                                                                                        args.client))
            else:
                print("Entries not found for system '{0}' in the KeePass Database".format(args.sid))
            return

        SAPPasswordManager.__try_to_connect(kp, entry, close_conn=False)

    @staticmethod
    def multi_login(args):
        kp = SAPPasswordManager.__open_kp()
        if not kp:
            return

        for entry in kp.get_all_entries():
            SAPPasswordManager.__try_to_connect(kp, entry, close_conn=True)
