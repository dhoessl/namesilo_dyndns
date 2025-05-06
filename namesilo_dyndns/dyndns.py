#!/usr/bin/env python3

from errno import ENOENT
from requests import get
from yaml import safe_load
from os import path, strerror
from namesilo_api import Domain, NamesiloAPIReturnError, RecordValueError
from logging import (
    getLogger, INFO, FileHandler, StreamHandler, Formatter,
    Logger
)


class NamesiloDyndns:
    def __init__(self):
        self.config = self.get_config()
        self.logger = self.get_logger()
        self.check_config()

    def run(self) -> None:
        self.logger.info("Starting DNS update")
        for domain in self.config["domains"]:
            domain_config = self.config["domains"][domain]
            if "key" not in domain_config:
                key_to_use = self.config["key"]
            else:
                key_to_use = domain_config["key"]
            domain_obj = Domain(key_to_use, domain)
            try:
                domain_obj.get_records()
            except NamesiloAPIReturnError:
                self.logger.error(
                    f"Error while fetching data for domain {domain}!"
                )
                exit(1)
            except RecordValueError as msg:
                self.logger.error(
                    "Faulty record type data fetched from Api! Create an "
                    "Issue on the github project including the following "
                    "message!"
                    + msg
                )
                exit(1)
            if domain_config["ipv4"]:
                self.set_record(
                    domain_obj,
                    "A",
                    self.get_my_ip(self.config["ipv4_server"]),
                    domain_config["subdomain"]
                )
            if domain_config["ipv6"]:
                self.set_record(
                    domain_obj,
                    "AAAA",
                    self.get_my_ip(self.config["ipv6_server"]),
                    domain_config["subdomain"]
                )
        self.logger.info("Finished DNS update")

    def get_my_ip(self, server) -> str:
        return get(server).json()["ip"]

    def set_record(self, domain_obj, rtype, ip, subdomain) -> None:
        record = domain_obj.get_host(subdomain, rtype)
        if record and record.value != ip:
            try:
                old_ip = record.value
                domain_obj.update_record_by_id(record.id, value=ip, ttl=3600)
                self.logger.info(f"{domain_obj.domain} | {old_ip} -> {ip}")
            except NamesiloAPIReturnError:
                self.logger.error(
                    "Some API error occured while updating {domain_obj.domain}"
                )
        elif not record:
            try:
                domain_obj.create_record(subdomain, rtype, ip, ttl=3600)
                self.logger.info(f"{domain_obj.domain} | None -> {ip}")
            except NamesiloAPIReturnError:
                self.logger.error(
                    "Some API error occured while updating {domain_obj.domain}"
                )
        else:
            self.logger.info(
                f"{domain_obj.domain} checked - {record.value} still correct"
            )

    def get_config(self) -> dict:
        location = None
        if path.exists("/etc/namesilo_dyndns/config.yaml"):
            location = "/etc/namesilo_dyndns/config.yaml"
        user_config_file = path.join(
            path.expanduser("~"), ".config", "namesilo_dyndns.yaml"
        )
        if path.exists(user_config_file):
            location = user_config_file
        if not location:
            raise FileNotFoundError(
                ENOENT, strerror(ENOENT),
                "/etc/namesilo_dyndns/config.yaml"
            )
        with open(location, "r") as yamlfile:
            config = safe_load(yamlfile)
        return config

    def check_config(self) -> dict:
        if "key" not in self.config:
            self.logger.error("Please specify your API key in the config")
            exit(1)
        if "ipv4_server" not in self.config:
            self.logger.warning("Setting default ipv4 check server")
            self.config["ipv4_server"] = "https://ip.dhoessl.de"
        if "ipv6_server" not in self.config:
            self.logger.warning("Setting default ipv6 check server")
            self.config["ipv6_server"] = "https://ipv6.dhoessl.de"
        if "domains" not in self.config:
            self.logger.error("domains key is missing in config")
            exit(1)
        for domain in self.config["domains"]:
            domain_config = self.config["domains"][domain]
            if (("ipv4" not in domain_config or not domain_config["ipv4"])
                    and ("ipv6" not in domain_config
                         or not domain_config["ipv6"])):
                self.logger.error(
                    "Please set atleast ipv4 or ipv6 as true for domain "
                    f"{domain} in your config file"
                )
                exit(1)
            if "subdomain" not in domain_config:
                self.logger.error(
                    f"Please set subdomain key in config for domain {domain}"
                )
                exit(1)
            if "ipv4" not in domain_config:
                self.config["domains"][domain]["ipv4"] = False
            if "ipv6" not in domain_config:
                self.config["domains"][domain]["ipv6"] = False

    def get_logger(self) -> Logger:
        verbose = self.config["verbose"] if "verbose" in self.config else False
        logger = getLogger(__name__)
        logger.setLevel(INFO)
        formatter = Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        file_handler = FileHandler("/var/log/dyndns.log")
        file_handler.setLevel(INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        if verbose:
            stream_handler = StreamHandler()
            stream_handler.setLevel(INFO)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
        return logger
