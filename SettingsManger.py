import json
import logging


class SettingsManager:
    def __init__(self, setting_filename="settings.json"):
        try:
            with open(setting_filename) as setting_file:
                self.settings = json.load(setting_file)
            self.is_valid = True
        except FileNotFoundError:
            logging.error("The settings file %s not found. Please Check your spelling." % setting_filename)
            self.is_valid = False

    def get_ali_client(self):
        return self.settings["aliClientSettings"]

    def get_log_settings(self):
        return self.settings["logFileName"]

    def get_ip_url(self, ip_type):
        return self.settings["getIPUrls"][ip_type]

    def get_domain_settings(self):
        return self.settings["domainSettings"]