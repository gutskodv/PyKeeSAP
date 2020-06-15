SAP_ID = "SAP ID"
SAP_CLIENT = "SAP Client"
SAP_LANGUAGE = "SAP Language"
FIELDS_MAPPING = {
    'sid': SAP_ID,
    'client': SAP_CLIENT,
    'langu': SAP_LANGUAGE}
ADD_OPTIONS = FIELDS_MAPPING.keys()

PYKEEPASS_GROUP = "PyKeeSAP"


class KeePassEntryNew:
    def __init__(self, entry=None):
        self.entry = entry
        self.title = None
        self.read_entry()

    def read_entry(self):
        if self.entry:
            self.username = self.entry.username
            self.password = self.entry.password
            self.title = self.entry.title
            self.properties = None
            self.sid = self.__get_option(SAP_ID)
            self.client = self.__get_option(SAP_CLIENT)
            self.langu = self.__get_option(SAP_LANGUAGE)

    def __str__(self):
        return self.title

    def __get_option(self, option_name):
        if not self.properties:
            self.properties = self.entry.custom_properties
        if option_name in self.properties.keys():
            return self.properties[option_name]

    @staticmethod
    def gen_new_title(**kwargs):
        out_str = "{0}-{1}".format(kwargs["user"], kwargs["sid"])
        if "client" in kwargs.keys() and kwargs["client"]:
            out_str += "-{0}".format(kwargs["client"])
        return out_str

    @staticmethod
    def create_group(kp):
        if kp is not None:
            group = kp.find_groups_by_path(group_path_str="/", first=True)
            if group is not None:
                kp.add_group(group, PYKEEPASS_GROUP)
                kp.save()

    def change_password(self, kp, new_pwd):
        self.password = new_pwd
        self.entry.password = new_pwd
        self.entry.touch(modify=True)
        print("Password for '{0}' updated".format(self))
        kp.save()

    def create_entry(self, kp,  **kwargs):
        group = kp.find_groups_by_name(group_name=PYKEEPASS_GROUP, first=True)
        if not group:
            KeePassEntryNew.create_group(kp)
            group = kp.find_groups_by_name(group_name=PYKEEPASS_GROUP, first=True)
            if not group:
                return

        if not (kwargs["user"] and kwargs["pwd"] and kwargs["sid"]):
            return
        try:
            created_entry = kp.add_entry(group, KeePassEntryNew.gen_new_title(**kwargs), kwargs["user"], kwargs["pwd"])
        except Exception as error:
            print(str(error))
        else:
            for key, value in kwargs.items():
                if key in ADD_OPTIONS:
                    if value:
                        created_entry.set_custom_property(FIELDS_MAPPING[key], value)

            kp.save()
            self.entry = created_entry
            self.read_entry()
            print("The user '{0}' created".format(self))
