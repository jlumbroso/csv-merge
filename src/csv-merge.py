#!/usr/bin/env python3

# Python 2
from __future__ import print_function

import argparse
import collections
import glob
import logging
import os
import sys

import yaml
from QuotedCSV import read_csv


###############################################################################

DEFAULT_YAML = "config.yaml"

###############################################################################


class _Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class SimpleColorFormatter(logging.Formatter):
    _title = {
        "DEBUG": "{END}[{BOLD}DBUG{END}]{END}".format(**_Color.__dict__),
        "INFO": "{END}[{BOLD}{GREEN}INFO{END}]{END}".format(**_Color.__dict__),
        "ERROR": "{END}[{BOLD}{RED}ERR {END}]{END}".format(**_Color.__dict__),
        "WARNING": "{END}[{BOLD}{BLUE}WARN{END}]{END}".format(**_Color.__dict__)
    }

    def normalizePath(self, path):
        abs_path = os.path.abspath(path)
        pwd_path = os.getcwd()
        return abs_path.replace(pwd_path, ".", 1)

    def formatMessage(self, msg: logging.LogRecord):
        header = self._title.get(msg.levelname, self._title.get("INFO"))
        return("{} {} (\"{}\", line {}): {}".format(
            header,
            msg.module,
            self.normalizePath(msg.filename),
            msg.lineno,
            msg.message
        ))


def setupLogging(name=None, level="INFO"):

    # Add the color handler to the terminal output
    handler = logging.StreamHandler()
    formatter = SimpleColorFormatter()
    handler.setFormatter(formatter)

    # Set logging level
    root = logging.getLogger(name=name)
    root.setLevel(os.environ.get("LOGLEVEL", level))

    # Add the color handler to the logger
    if name == None:
        root.addHandler(handler)

    return root


logger = setupLogging()

###############################################################################
parser = argparse.ArgumentParser()

parser.add_argument(
    "-y",
    help="Name of the YAML job description.")

parser.add_argument(
    "-p",
    help="Name of the YAML patch file (optional).")

parser.add_argument(
    "--verbose",
    action="store_true",
    help="Display informational messages.")


def process_command_line(parser):
    logger.debug("Parsing command line input")

    args, _unknown = parser.parse_known_args()
    params = vars(args)

    if params["verbose"]:
        logger.info("Logger: Setting to DEBUG")
        logger.setLevel("DEBUG")

    logger.debug("Command Line: {}".format(params))

    yaml_file = params.get("y", DEFAULT_YAML) or DEFAULT_YAML

    logger.debug("Configuration File: '{}'".format(yaml_file))

    if not os.path.exists(yaml_file):
        logger.error(
            "Configuration File: File does not exist")
        sys.exit(1)

    config = dict()
    try:
        config = yaml.load(open(yaml_file))
    except Exception:
        logger.exception("Configuration File: Error while reading")

    logger.debug("Configuration File: {}".format(config))

    # Complete config with command-line parameters
    config["yaml"] = yaml_file
    if params["p"]:
        config["patch"] = params["p"]

    logger.debug("Configuration: {}".format(config))

    return config


# Loading YAML file
config = process_command_line(parser)

# Some default properties

ip_default_userkey = config.get(
    "defaults", dict()).get("username", "Username")

ip_default_valuekey = config.get(
    "defaults", dict()).get("value", "Value")

ip_default_path = config.get(
    "defaults", dict()).get("path", "")

op_default_userkey = config.get(
    "output", dict()).get("username", "Username")

# Processing files one by one

pattern_list = config.get("sources", dict()).keys()
counter = 0

full_data = collections.OrderedDict()
full_headers = [op_default_userkey]

for p in pattern_list:

    # Locate file
    fp = os.path.join(ip_default_path, p)
    results = glob.glob(fp)
    logger.debug("Globbing '{}' yielded: {}.".format(fp, results))
    if len(results) == 0:
        continue

    # Last in lexicographic order
    results.sort()
    last_result = results[-1]

    filename = last_result

    # Info
    logger.debug(">>> Reading {}".format(filename))

    # Get parameters
    counter += 1
    unique_header = "Header{:0<3}".format(counter)

    userkey = config["sources"][p].get("username", ip_default_userkey)
    valuekey = config["sources"][p].get("value", ip_default_valuekey)
    header = config["sources"][p].get("caption", unique_header)

    # Expand the header list
    full_headers.append(header)

    # Obtain data
    rows = read_csv(filename, as_dict=True)

    # Insert it into full-structure
    for row in rows:
        user = row[userkey]
        value = row[valuekey]

        if user.strip() == "":
            continue

        full_data[user] = full_data.get(user, collections.OrderedDict())
        full_data[user][header] = value

# Patch the data
patch_pattern = config.get("patch")
if patch_pattern:
    patch_files = glob.glob(patch_pattern)
    logger.debug("Candidates for patch file: {}".format(patch_files))
    patch_file = patch_files[-1]
    logger.debug(
        "Running last one by lexicographic order: {}".format(patch_file))
    rows = read_csv(patch_file, as_dict=True)

    logger.debug("Patch: {}".format(rows))

    for patch in rows:
        user = patch.get("Username", None)
        header = patch.get("Caption", None)
        patched_value = patch.get("Value", None)

        if user == None or header == None or value == None:
            continue

        prev_value = full_data.get(user, dict()).get(header, None)

        if not user in full_data:
            logger.debug("Adding new user '{}' by patch".format(user))
            full_data[user] = dict()

        full_data[user][header] = patched_value
        logger.debug("Patch: data [{}.{}] {} => {}".format(
            user,
            header,
            prev_value,
            patched_value
        ))

# Output the aggregated data
print(",".join(full_headers))
for user in full_data.keys():
    userdata = full_data[user]
    userdata[op_default_userkey] = user
    print(",".join(map(lambda colname: userdata.get(colname, ""), full_headers)))
