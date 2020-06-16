import argparse
import os
import pykeesap
from pykeesap.password_manager import SAPPasswordManager


def cmd():
    path = os.path.join(os.path.dirname(pykeesap.__file__), pykeesap.SETTINGS_FILE)
    parser = argparse.ArgumentParser(prog='PyKeeSAP', description="settings.ini path: '{0}'".format(path))
    subparsers = parser.add_subparsers(help='Sub-commands:')

    parser_print = subparsers.add_parser('print', help='print entries in the KeePass Database')
    parser_print.add_argument('-s', '--sid', type=str, help='SAP ID')
    parser_print.set_defaults(func=SAPPasswordManager.print_users)

    parser_create = subparsers.add_parser('create', help='create new entry in the KeePass Database')
    parser_create.add_argument('sid', type=str, help='SAP ID')
    parser_create.add_argument('-u', '--user', type=str, help='SAP Username', required=True)
    parser_create.add_argument('-p', '--pwd', type=str, help='password', required=True)
    parser_create.add_argument('-c', '--client', type=str, help='SAP Client')
    parser_create.add_argument('-l', '--langu', type=str, help='SAP Language')
    parser_create.set_defaults(func=SAPPasswordManager.create_entry)

    parser_delete = subparsers.add_parser('delete', help='delete entry in the KeePass Database')
    parser_delete.add_argument('title', type=str, help='entry title in the KeePass Database')
    parser_delete.set_defaults(func=SAPPasswordManager.delete_entry)

    parser_changekeepasspwd = subparsers.add_parser('changekeepasspwd',
                                                    help='update password of entry in the KeePass Database')
    parser_changekeepasspwd.add_argument('title', type=str, help='entry title in KeePass')
    parser_changekeepasspwd.add_argument('-p', '--pwd', type=str, help='new password', required=True)
    parser_changekeepasspwd.set_defaults(func=SAPPasswordManager.change_keepass_password)

    parser_login = subparsers.add_parser('login', help='login to SAP system')
    parser_login.add_argument('sid', type=str, help='SAP SID')
    parser_login.add_argument('-c', '--client', type=str, help='SAP Client')
    parser_login.add_argument('-u', '--user', type=str, help='SAP Username')
    parser_login.add_argument('-t', '--title', type=str, help='entry title in the KeePass Database')
    parser_login.set_defaults(func=SAPPasswordManager.login)

    parser_changepwd = subparsers.add_parser('changepwd', help='change password to SAP system user')
    parser_changepwd.add_argument('title', type=str, help='entry title in the KeePass Database')
    parser_changepwd.set_defaults(func=SAPPasswordManager.change_system_password)

    parser_recursive_login = subparsers.add_parser('multilogin', help='verify all entries in the KeePass Database')
    parser_recursive_login.set_defaults(func=SAPPasswordManager.multi_login)

    parser_multichangepwd = subparsers.add_parser('multichangepwd', help='change password to all entries in the '
                                                                         'KeePass Database')
    parser_multichangepwd.set_defaults(func=SAPPasswordManager.multi_change_password)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
