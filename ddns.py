from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from urllib.request import urlopen
import json
import logging


def update_record(record_id, domain_name, subdomain_name, record_type, record_value, ali_client):
    request = UpdateDomainRecordRequest()
    request.set_accept_format("json")
    request.set_RecordId(record_id)
    request.set_RR(subdomain_name)
    request.set_Type(record_type)
    request.set_Value(record_value)
    response = json.loads(ali_client.do_action(request))
    error_code = response.get('Code', "No error code")
    if error_code == "No error code":
        print("Successfully updated record for %s" % (subdomain_name+"."+domain_name))
        logging.info("Successfully updated record for %s" % (subdomain_name+"."+domain_name))
    else:
        print("Update for record for %s failed. Response json: %s" % (subdomain_name+"."+domain_name, response))
        logging.error("Update for record for %s failed. Recommend: %s" % 
                      (subdomain_name+"."+domain_name, response.get("Recommend", "None")))


def change_single_domain(subdomain_name, domain_name, record_type, ip_value, ali_client):
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format("json")
    request.set_DomainName(domain_name)
    request.set_SubDomain(subdomain_name+"."+domain_name)
    request.set_Type(record_type)
    response = ali_client.do_action(request)
    domain_list = json.loads(response)

    if domain_list['TotalCount'] == 0:
        logging.error("The Domain %s doesn't have %s record." % (subdomain_name+"."+domain_name, record_type))

    elif domain_list['TotalCount'] == 1:
        if domain_list["DomainRecords"]["Record"][0]["Value"].strip() != ip_value.strip():
            update_record(domain_list['DomainRecords']['Record'][0]['RecordId'], domain_name, subdomain_name,
                          record_type, ip_value, ali_client)
        else:
            print("The ip address in the record is the same as this machine. Record for %s.%s unchanged." %
                  (subdomain_name, domain_name))
            logging.info("Record for %s did not change since is it the same as the machine." %
                         (subdomain_name + "." + domain_name))
    else:
        print("I don't know what happened. Go check the record on the console.")
        logging.error("There are more than 1 record for $s." % (subdomain_name + "." + domain_name))


def main():
    with open("settings.json") as fl:
        settings = json.loads(fl.read())

    LOG_LEVEL = settings["logLevel"]
    if LOG_LEVEL.lower() == "debug":
        LOG_LEVEL = logging.DEBUG
    elif LOG_LEVEL.lower() == "info":
        LOG_LEVEL = logging.INFO
    elif LOG_LEVEL.lower() == "warning":
        LOG_LEVEL = logging.WARNING
    else:
        LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=settings["logFileName"], level=LOG_LEVEL, format=LOG_FORMAT)

    logging.info("DDNS script started.")
    access_key_id = settings["aliClientSettings"]["accessKeyId"]
    access_secret = settings["aliClientSettings"]["accessSecret"]
    aliyun_client = AcsClient(access_key_id, access_secret, 'cn-hangzhou')

    if settings["ipv4ddnsSettings"]["enabled"]:
        logging.info("Start ipv4 ddns")
        current_v4_ip = urlopen(settings["ipv4ddnsSettings"]["getIPUrl"]).read()
        current_v4_ip = str(current_v4_ip, encoding="utf-8")
        logging.info("Got current ipv4 address: %s" % current_v4_ip)
        v4_domains = settings["ipv4ddnsSettings"]["domains"]
        for domain_set in v4_domains:
            v4_domain = domain_set["domain"]
            v4_subdomains = domain_set["subdomains"]
            for v4_subdomain in v4_subdomains:
                change_single_domain(v4_subdomain, v4_domain, "A", current_v4_ip, aliyun_client)
        logging.info("DDNS for ipv4 ended")
    else:
        logging.info("DDNS for ipv4 disabled")

    if settings["ipv6ddnsSettings"]["enabled"]:
        logging.info("Start ipv6 ddns")
        current_v6_ip = urlopen(settings["ipv6ddnsSettings"]["getIPUrl"]).read()
        current_v6_ip = str(current_v6_ip, encoding="utf-8")
        logging.info("Got current ipv6 address: %s" % current_v6_ip)
        if settings["ipv6ddnsSettings"]["UseSettingsInIPv4Section"]:
            logging.info("Load domain settings from IPv4 Section")
            v6_domains = settings["ipv4ddnsSettings"]["domains"]
        else:
            v6_domains = settings["ipv6ddnsSettings"]["domains"]
        for v6_domain_set in v6_domains:
            v6_domain = v6_domain_set["domain"]
            v6_subdomains = v6_domain_set["subdomains"]
            for v6_subdomain in v6_subdomains:
                change_single_domain(v6_subdomain, v6_domain, "AAAA", current_v6_ip, aliyun_client)
        logging.info("DDNS for ipv6 ended")
    else:
        logging.info("DDNS for ipv6 disabled")


    logging.info("DDNS script ended.")


if __name__ == "__main__":
    main()
