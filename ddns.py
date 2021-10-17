#    Copyright 2021 un-lock-able
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from urllib.request import urlopen
import json
import logging


def create_record(subdomain_name, domain_name, record_type, record_value, ali_client):
    request = AddDomainRecordRequest()
    request.set_accept_format("json")
    request.set_DomainName(domain_name)
    request.set_RR(subdomain_name)
    request.set_Type(record_type)
    request.set_Value(record_value)
    response = ali_client.do_action(request)
    response = json.loads(response)
    error_code = response.get('Code', None)
    if error_code is None:
        logging.info("Successfully created an %s record for %s." % (record_type, subdomain_name+"."+domain_name))
    else:
        logging.warning("Failed to create an %s record for %s. Recommended actions from aliyun: %s." %
                        (record_type, subdomain_name+"."+domain_name, response.get("Recommend", "None")))


def update_record(subdomain_name, domain_name, record_type, record_value, record_id, ali_client):
    request = UpdateDomainRecordRequest()
    request.set_accept_format("json")
    request.set_RecordId(record_id)
    request.set_RR(subdomain_name)
    request.set_Type(record_type)
    request.set_Value(record_value)
    response = ali_client.do_action(request)
    response = json.loads(response)
    error_code = response.get('Code', None)
    if error_code is None:
        logging.info("Successfully updated the record for %s." % (subdomain_name+"."+domain_name))
    else:
        logging.warning("Failed to update the record for %s. Recommended actions from aliyun: %s." %
                        (subdomain_name+"."+domain_name, response.get("Recommend", "None")))


def change_single_domain(subdomain_name, domain_name, record_type, ip_value, allow_new, ali_client):
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format("json")
    request.set_DomainName(domain_name)
    request.set_SubDomain(subdomain_name+"."+domain_name)
    request.set_Type(record_type)
    response = ali_client.do_action(request)
    domain_list = json.loads(response)

    if domain_list['TotalCount'] == 0:
        if allow_new:
            logging.info("The Domain %s doesn't have %s record. Will create a new record for it." %
                         (subdomain_name+"."+domain_name, record_type))
            create_record(subdomain_name, domain_name, record_type, ip_value, ali_client)

    elif domain_list['TotalCount'] == 1:
        if domain_list["DomainRecords"]["Record"][0]["Value"].strip() != ip_value.strip():
            update_record(subdomain_name, domain_name, record_type, ip_value,
                          domain_list['DomainRecords']['Record'][0]['RecordId'], ali_client)
        else:
            logging.info("Record for %s did not change since is it the same as the machine." %
                         (subdomain_name + "." + domain_name))
    else:
        logging.error("There are more than 1 record for %s. Record for %s was left unchanged." %
                      (subdomain_name + "." + domain_name, subdomain_name + "." + domain_name))


def main():
    with open("settings.json") as fl:
        settings = json.loads(fl.read())

    log_level = settings["logSettings"]["logLevel"]
    if log_level.lower() == "debug":
        log_level = logging.DEBUG
    elif log_level.lower() == "info":
        log_level = logging.INFO
    elif log_level.lower() == "warning":
        log_level = logging.WARNING
    else:
        log_level = logging.DEBUG
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=settings["logSettings"]["logFileName"], level=log_level, format=log_format)

    logging.info("DDNS script started.")
    access_key_id = settings["aliClientSettings"]["accessKeyId"]
    access_secret = settings["aliClientSettings"]["accessSecret"]
    aliyun_client = AcsClient(access_key_id, access_secret, 'cn-hangzhou')

    if settings["ipv4ddnsSettings"]["enabled"]:
        logging.info("Start ipv4 ddns.")

        v4_create_new = settings["ipv4ddnsSettings"]["createNewRecord"]
        if v4_create_new:
            logging.info("The script will create a new record when there is no record present.")
        else:
            logging.info("The script will not create a new record when there is no record present.")

        current_v4_ip = urlopen(settings["ipv4ddnsSettings"]["getIPUrl"]).read()
        current_v4_ip = str(current_v4_ip, encoding="utf-8").strip()
        logging.info("Got current ipv4 address: %s." % current_v4_ip)

        v4_domains = settings["ipv4ddnsSettings"]["domains"]
        for domain_set in v4_domains:
            v4_domain = domain_set["domain"]
            v4_subdomains = domain_set["subdomains"]
            for v4_subdomain in v4_subdomains:
                change_single_domain(v4_subdomain, v4_domain, "A", current_v4_ip, v4_create_new, aliyun_client)
        logging.info("DDNS for ipv4 ended.")
    else:
        logging.info("DDNS for ipv4 disabled.")

    if settings["ipv6ddnsSettings"]["enabled"]:
        logging.info("Start ipv6 ddns.")

        v6_create_new = settings["ipv4ddnsSettings"]["createNewRecord"]
        if v6_create_new:
            logging.info("The script will create a new record when there is no record present.")
        else:
            logging.info("The script will not create a new record when there is no record present.")

        current_v6_ip = urlopen(settings["ipv6ddnsSettings"]["getIPUrl"]).read()
        current_v6_ip = str(current_v6_ip, encoding="utf-8").strip()
        logging.info("Got current ipv6 address: %s." % current_v6_ip)

        if settings["ipv6ddnsSettings"]["UseSettingsInIPv4Section"]:
            logging.info("Load domain settings from IPv4 Section")
            v6_domains = settings["ipv4ddnsSettings"]["domains"]
        else:
            v6_domains = settings["ipv6ddnsSettings"]["domains"]

        for v6_domain_set in v6_domains:
            v6_domain = v6_domain_set["domain"]
            v6_subdomains = v6_domain_set["subdomains"]
            for v6_subdomain in v6_subdomains:
                change_single_domain(v6_subdomain, v6_domain, "AAAA", current_v6_ip, v6_create_new, aliyun_client)
        logging.info("DDNS for ipv6 ended.")
    else:
        logging.info("DDNS for ipv6 disabled.")

    logging.info("DDNS script ended.")


if __name__ == "__main__":
    main()
