from DomainRecordChanger import DomainRecordChanger
from SettingsManger import SettingsManager
from aliyunsdkcore.client import AcsClient
from urllib.request import urlopen
import logging
import sys


class DDNS:
    settings_manager = SettingsManager()
    ali_client_settings = None
    ali_client = None
    ip_url = None
    domain_settings = None

    @staticmethod
    def init_logging():
        log_settings = DDNS.settings_manager.get_log_settings()
        log_level = log_settings["logLevel"]
        if log_level.lower() == "debug":
            log_level = logging.DEBUG
        elif log_level.lower() == "info":
            log_level = logging.INFO
        elif log_level.lower() == "warning":
            log_level = logging.WARNING
        else:
            log_level = logging.DEBUG
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(filename=log_settings["logFileName"],level=log_level,format=log_format)

    @staticmethod
    def read_settings():
        DDNS.ali_client_settings = DDNS.settings_manager.get_ali_client()
        DDNS.ip_url = DDNS.settings_manager.get_ip_url()
        DDNS.domain_settings = DDNS.settings_manager.get_domain_settings()

    @staticmethod
    def main():
        DDNS.init_logging()
        DDNS.read_settings()
        if not DDNS.settings_manager.is_valid:
            logging.error("Bad configuration.")
            sys.exit(1)
        else:
            pass

        DDNS.ali_client = AcsClient(DDNS.ali_client_settings["accessKeyId"],
                                    DDNS.ali_client_settings["accessKeyId"])

        for single_domain_config in DDNS.domain_settings:
            dm = DomainRecordChanger(DDNS.ali_client, DDNS.ip_url, single_domain_config)
            dm.start_ddns()

if __name__ == "__main__":
    DDNS.main()