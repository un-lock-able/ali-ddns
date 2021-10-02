from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from urllib.request import urlopen
import json
import logging

accessKeyId = ""
accessSecret = ""
domain = ""
subdomains = []


def update(RecordId, RR, Type, Value, aliclient):
    request = UpdateDomainRecordRequest()
    request.set_accept_format("json")
    request.set_RecordId(RecordId)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    response = json.loads(aliclient.do_action(request))
    error_code = response.get('Code', "No error code")
    if error_code == "No error code":
        print("Successfully updated record for %s" % (RR+"."+domain))
        logging.info("Successfully updated record for %s" % (RR+"."+domain))
    else:
        print("Update for record for %s failed. Response json: %s" % (RR+"."+domain, response))
        logging.error("Update for record for %s failed. Recommend: %s" % 
                      (RR+"."+domain, response.get("Recommend", "None")))


def changeSingleDomain(subDomainName, ipValue, aliclient):
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format("json")
    request.set_DomainName(domain)
    request.set_SubDomain(subDomainName+"."+domain)
    request.set_Type("AAAA")
    response = aliclient.do_action(request)
    domain_list = json.loads(response)

    if domain_list['TotalCount'] == 0:
        logging.error("The Domain %s doesn't have AAAA record." % (subDomainName+"."+domain))

    elif domain_list['TotalCount'] == 1:
        if domain_list["DomainRecords"]["Record"][0]["Value"].strip() != ipValue.strip():
            update(domain_list['DomainRecords']['Record'][0]['RecordId'], subDomainName, "AAAA", ipValue, aliclient)
        else:
            print("The ip address in the record is the same as this machine. Record for %s.%s unchanged." %
                  (subDomainName, domain))
            logging.info("Record for %s did not change since is it the same as the machine." %
                         (subDomainName + "." + domain))
    else:
        print("I don't know what happened. Go check the record on the console.")
        logging.error("There are more than 1 record for $s." % (subDomainName + "." + domain))


def main():
    global accessKeyId, accessSecret, domain, subdomains
    with open("settings.json") as fl:
        settings = json.loads(fl.read())
    accessKeyId = settings["accessKeyId"]
    accessSecret = settings["accessSecret"]
    domain = settings["domain"]
    subdomains = settings["subdomains"]
    client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')

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

    currentIP = urlopen("http://v6.ip.zxinc.org/getip").read()
    currentIP = str(currentIP, encoding="utf-8")
    print("Got current ipv6 address: %s" % currentIP)
    logging.info("DDNS script started.")
    logging.info("Got current ipv6 address: %s" % currentIP)

    for subdomain in subdomains:
        changeSingleDomain(subdomain, currentIP, client)
    logging.info("DDNS script ended.")


if __name__ == "__main__":
    main()
