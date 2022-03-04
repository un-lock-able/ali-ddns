# Copyright 2022 un-lock-able
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from DomainRecordChanger import DomainRecordChanger
from SettingsManager import SettingsManager
from aliyunsdkcore.client import AcsClient
import logging
import sys


class DDNS:
    settings_manager = None
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
    def main(settings_path="aliddnsSettings.json"):
        DDNS.settings_manager = SettingsManager(settings_path)
        if not DDNS.settings_manager.is_valid:
            sys.exit(1)
        DDNS.init_logging()
        DDNS.read_settings()
        if not DDNS.settings_manager.is_valid:
            logging.error("Bad configuration.")
            sys.exit(1)
        else:
            pass
        logging.info("--------DDNS script started--------")
        DDNS.ali_client = AcsClient(DDNS.ali_client_settings["accessKeyId"],
                                    DDNS.ali_client_settings["accessSecret"])

        for single_domain_config in DDNS.domain_settings:
            dm = DomainRecordChanger(DDNS.ali_client, DDNS.ip_url, single_domain_config)
            dm.start_ddns()
        logging.info("---------DDNS script ended---------")