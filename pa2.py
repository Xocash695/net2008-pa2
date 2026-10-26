# Name: Akash Kallumkal
# Student ID: 041267997
import sys

def main():
    device_xml, policy_yaml = cmd_args()
    print("The device file", device_xml, "The policy file:", policy_yaml)

def cmd_args(): # used to grab the commandline arguments
    """Get the names of the files passed in """
    numArg = len(sys.argv) # get the number of arguments
    if numArg != 3 :
        print("usage: python pa2.py DEVICES.xml POLICY.yaml") # show the correct usage
        sys.exit(2) #give the exit code 2 if not correct
    return sys.argv[1], sys.argv[2] # return 2 items


if __name__ == "__main__":
    main()
