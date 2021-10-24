import json
import logging


class SettingsManager:
    def __init__(self):
        try:
            with open("aliddnsSettings.json") as setting_file:
                self.settings = json.load(setting_file)
            self.is_valid = True
        except FileNotFoundError:
            logging.error("The settings file aliddnsSettings.json not found. Please Check your spelling.")
            self.is_valid = False

    def get_ali_client(self):
        return self.settings["aliClientSettings"]

    def get_log_settings(self):
        return self.settings["logFileName"]

    def get_ip_url(self, ip_type):
        return self.settings["getIPUrls"][ip_type]

    def get_domain_settings(self):
        return self.settings["domainSettings"]