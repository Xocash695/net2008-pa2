# Name: Akash Kallumkal
# Student ID: 041267997
import sys
import pathlib
import xml.etree.ElementTree as ET # xml parsing


def main():
    device_xml, policy_yaml = cmd_args()
    print("The device file", device_xml, "The policy file:", policy_yaml)
    # check that the files exist
    file_exists(device_xml)
    file_exists(policy_yaml)
    root = get_inventory("devices.xml")
    print(root.tag)                      # inventory
    print(root.get("site"))              # ott-dc1
    print(len(root.findall("device")))   # 6


def get_inventory(filename):
    with open(filename) as f:
        root = ET.parse(f).getroot() # parse the xml file
        return root


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
