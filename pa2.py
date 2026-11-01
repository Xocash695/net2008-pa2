# Name: Akash Kallumkal
# Student ID: 041267997
import sys
import pathlib
import xml.etree.ElementTree as ET # xml parsing
import json

import yaml


class AuditError(Exception):
    """Raised when a input file is not correct or is invalid"""


class Device:
    """A single device from the network"""
    def __init__(self, data):
        self.id = data.get("id")
        self.role = data.get("role") #get gets the data of that element
        self.os = data.get("os")
        findowner = data.find("owner") # find basically gets the child elements of xml
        self.owner = ""
        if findowner is not None and findowner.text: # .text helps get the text inbetween the tag
            self.owner = findowner.text.strip()
        self.interfaces = [(i.get("name"), i.get("status")) for i in data.findall("interface")]

    def has_owner(self):
        """Will return true if the device has an owner"""
        return self.owner != ""
    def interface_counts(self):
        """Return the number interfaces with each state """
        totals = {"up": 0, "down": 0, "other": 0}

        for interface, status in self.interfaces:
            if status == "down" or status == "up":
                totals[status] += 1
            else:
                totals["other"] += 1
        return totals

def count_interfaces(devices):
    """ Counts the total number of interfaces by adding everything up from each device"""
    total = {"up": 0, "down": 0, "other": 0}
    for device in devices:
       for key, value in device.interface_counts().items():
           total[key] += value
    return total

def count_roles(devices):
    """Count the number of roles that exist, if the role doesn't exist create it otherwise it updates existing role """
    roles = {}
    for d in devices:
        current = roles.get(d.role, 0)
        roles[d.role] = current + 1
    return roles


def main():
    device_xml, policy_yaml = cmd_args()
    # check that the files exist
    file_exists(device_xml)
    file_exists(policy_yaml)
    root = get_inventory(device_xml)
    site,skipped, devices = parse_inventory(root)
    policy = get_policy(policy_yaml)
    violations = (
        check_unknown_role(devices, policy)
        + check_missing_owner(devices, policy)
        + too_many_down(devices, policy)
        + check_os_outdated(devices, policy)
    )
    flagged = {v["device"] for v in violations} # bascially are getting all the device ids from the violations dict
    compliant = [] # keep all the compilant
    for device in devices:
        if device.id not in flagged:
            compliant.append(device.id)
    compliant = sorted(compliant)

    report = {
        "site": site,
        "total_devices": len(devices),
        "skipped_devices": skipped,
        "roles": count_roles(devices),
        "interfaces": count_interfaces(devices),
        "violations": violations,
        "compliant": compliant
    }
    create_report(report)


def get_inventory(devices_xml):
    """open the inventory file and pass it"""
    try:
        with open(devices_xml) as f:
            root = ET.parse(f).getroot() # parse the xml file
            return root
    except ET.ParseError:
            raise AuditError(f"Invalid XML file: {devices_xml}")



def parse_inventory(root):
    """Takes the inventory and turns the xml in device objects"""
    site = root.get("site")
    devices = []
    skipped = 0
    for dev in root.findall("device"):
        if dev.get("id") is None: # if there is no id provided
            skipped += 1
            continue
        devices.append(Device(dev))
    return site,skipped,devices

def get_policy(policy_yaml):
    """Opens the the policy file and checks if there is something if there is nothing then an empty dict is given"""
    try:
        with open(policy_yaml) as f:
            loaded = yaml.safe_load(f)
    except yaml.YAMLError:
            raise AuditError(f"Invalid YAML file: {policy_yaml}")
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise AuditError(f"Policy must be a mapping: {policy_yaml}")
    return loaded


def check_unknown_role(devices, policy):
    """Checking for unknown roles"""
    violations = []
    min_os = policy.get("min_os")
    if min_os is None:
        return violations
    for device in devices:
        role = device.role
        if role not in min_os:
            violations.append({
                "device": device.id,
                "type": "unknown_role",
                "role": role
            })

    return violations

def check_missing_owner(devices, policy):
    """checking for a missing owner and returns a dict with the missing owners"""
    missing = []
    require_owner = policy.get("require_owner")
    if not require_owner:
        return missing
    for device in devices:
        if not device.has_owner():
            missing.append({
                "device": device.id,
                "type": "missing_owner",
            })
    return missing


def too_many_down(devices, policy):
    """Check if too many interfaces on the device are in the down state"""
    total_down = []
    max_down_interfaces = policy.get("max_down_interfaces")
    if max_down_interfaces is None:
        return total_down
    for device in devices:
        down = device.interface_counts()["down"]
        if down > max_down_interfaces:
            total_down.append({
                "device": device.id,
                "type": "too_many_down",
                "down": down
            })
    return total_down




def check_os_outdated(devices, policy):
    def version_lt(found, required):
        """made to help make it easier to do os outdated check because the versions don't all have the same number of digits"""
        found_parts = [int(p) for p in found.split(".")] # split everything into integers by the dot ex [1,2,3]
        required_parts = [int(p) for p in required.split(".")]
        length = max(len(found_parts), len(required_parts)) # find the bigger number here
        found_parts.extend([0] * (length - len(found_parts))) #adding zeros if nessary ex comparing 1.9 to 1.9.0
        required_parts.extend([0] * (length - len(required_parts))) # star means to repeat
        return found_parts < required_parts # return if true it is less than required

    """Checking if the device meets the minimum os requirements"""
    violations = []
    min_os = policy.get("min_os")
    if min_os is None:
        return violations
    for device in devices:
        found_os = device.os
        role = device.role
        required = min_os.get(role)
        if required is None:
            continue
        if version_lt(found_os, required):
            violations.append({
                "device": device.id,
                "type": "os_outdated",
                "found": found_os,
                "required": required
            })
    return violations

def cmd_args(): # used to grab the commandline arguments
    """Get the names of the files passed in """
    numArg = len(sys.argv) # get the number of arguments
    if numArg != 3 :
        print("usage: python pa2.py DEVICES.xml POLICY.yaml") # show the correct usage
        sys.exit(2) #give the exit code 2 if not correct
    return sys.argv[1], sys.argv[2] # return 2 items

def file_exists(filename):
    """Checks if the file actually exists"""
    if not pathlib.Path(filename).exists():
        raise AuditError(f"File does not exist: {filename}")



def create_report(report):
    """Creates the final report"""
    try:
        with open("audit.json", "w") as f:
            json.dump(report, f, indent=2)
    except OSError:
            raise AuditError("Could not write audit.json")

if __name__ == "__main__":
    main()
