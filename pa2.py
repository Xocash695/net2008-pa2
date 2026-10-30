# Name: Akash Kallumkal
# Student ID: 041267997
import sys
import pathlib
import xml.etree.ElementTree as ET # xml parsing



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



def main():
    device_xml, policy_yaml = cmd_args()
    print("The device file", device_xml, "The policy file:", policy_yaml)
    # check that the files exist
    file_exists(device_xml)
    file_exists(policy_yaml)
    root = get_inventory("devices.xml")
    # debug stuff to be removed later
    print(root.tag)                      # inventory
    print(len(root.findall("device")))   # 6
    site, devices = parse_inventory(root)
    print(site)
    for d in devices:
        print(d.id, d.interface_counts())


def get_inventory(filename):
    with open(filename) as f:
        root = ET.parse(f).getroot() # parse the xml file
        return root


def parse_inventory(root):
    site = root.get("site")
    devices = []
    skipped = 0
    for dev in root.findall("device"):
        if dev.get("id") is None:
            skipped += 1
            continue
        devices.append(Device(dev))
    return site,devices


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
        print("File does not exist: ", filename)
        sys.exit(1)



if __name__ == "__main__":
    main()
