#!/usr/bin/python

from collections import defaultdict
import datetime
import os
import sys
import argparse

import boto3
import pytz


"""
get AWS instance state by tag owner=$USER and display with bitbar.
0  : pending
16 : running
32 : shutting-down
48 : terminated
64 : stopping
80 : stopped
"""

# override error method to print help message
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        print("")
        self.print_help()
        print("")
        sys.exit(1)

class myAWS:
    def __init__(self, bit_bar_display=True):
        self.bit_bar_display=bit_bar_display
        try:
            # ec2 context
            ec2 = boto3.resource('ec2')

            # set filter by owner tag, ignore terminated instances
            instance_filter = [{
                'Name': 'tag:owner',
                'Values': [os.environ['USER']]}]
            # do not count terminated
            instance_filter.append({
                'Name': 'instance-state-name',
                'Values': ['pending', 'running', 'shutting-down', 'stopping', 'stopped']})
            my_instances = ec2.instances.filter(Filters=instance_filter)

            # instance state and instance time dictionaries
            self.state_dict = defaultdict(int)
            self.time_dict = defaultdict(lambda: datetime.datetime.now(pytz.utc))

            for instance in my_instances:
                self.state_dict[instance.state['Name']] += 1
                if instance.launch_time < self.time_dict[instance.state['Name']]:
                    self.time_dict[instance.state['Name']] = instance.launch_time
        except:
            # no instances with owner = USER tag
            if self.bit_bar_display:
                print (":no_entry_sign: 0 Instances|size=12 color=LightSlateGray\n---\nAWS owner tag: {0}|color=SteelBlue".format(os.environ['USER']))
            else:
                print ("0 Instances for AWS owner tag: {0}".format(os.environ['USER']))
            sys.exit(1)

    def doOutput(self):
        state_bitbar_format_str=""
        if self.bit_bar_display: # format for bitbar
            if 'running' in self.state_dict:
                print (
                    "{0}|size=14 color=FireBrick image='iVBORw0KGgoAAAANSUhEUgAAABEAAAAQCAYAAADwMZRfAAAAAXNSR0IArs4c6QAAAl9JREFUOBF1kj9oU1EUxs9LXt5LTUyatIQkVKRDjOCoLp2MQwehoEuGgl1c7FBwctBNl05C1y52Eqy4FEUrVKFFtJmEtrYQoSAEs6RFHPI/z+877z54FD1w37vv3fv9znfPuZaciT/1+pXI/v5zz3Guf3r0WMp2VEqJhEivL3Ln9hdZWHgm+fxry7K8QGoFk5Ojo/vJZvPBt5evGtna15vF9LhstVpSHhsD5JyIB81oJDIxKVK5ITI7uyil0ipgI6u1t3chtlurHb59ky+fnEq905asG5eC48jWKSCJJCBJHyIADQHqw1UqJXLtakfm5y/Zze1dN/NiLa+Z0ml/s22LuK6IHfMHgLrOA8TwgDuF7ezEZXratQV7LVK7HREHoh4AFHEQEuMwED08IAoDMI7/SAYFglmHA2xmdsAoUrEBcp01UTVInBM4GFJtIOiAAkhuY/DbxTsSwZwgDIWoxn/wO4p1dcIstD6AE9qnwME/OtFvrAU1CTHUlIciI6BAUNTtGSEhEOqRzBzd0vbq5tCDiREoLABR2KeQR2B2tWnmelTAeEfCwRKZLhonELD30ZALhQHOt3bnDIRA3hmEgWBjG0WiG7rSOrEmWCYgDrd0wuxBaGHxA3sjv0Uaksvd8niBgrYGIIUARDfqCG+tl3GcOn8ASMOeqVbbgL87WF+/aHe7Gfl+eE+GwyUfSJEZI2S1cDkITia2pVi8a83N/aQxvYOBQ76bm5uJ/vFxMTOZm/n44f3a5eyElAoFH5AZfypTU0+sSsVvS1j4v/nnlZWHP5aXf3kbG1XP81C0f8dfrmqv0yR5iiYAAAAASUVORK5CYII='".format(
                    self.state_dict['running']))
            else:
                print(
                    "{0}|size=12 color=LightSlateGray image='iVBORw0KGgoAAAANSUhEUgAAABQAAAASCAMAAABsDg4iAAAA21BMVEUAAAD////t7e3n5+fr6+v29vb39/f4+Pj////y8vLT09PLy8vb29v7+/vPz8/19fXX19e6urra2trm5ubq6ure3t76+vrAwMDp6enj4+Pi4uLc3NzHx8fs7Oze3t7f39/o6OjR0dGlpaWxsbHf39+4uLi+vr69vb3Hx8d7e3t8fHx9fX2AgICCgoKFhYWLi4uRkZGSkpKZmZmbm5ucnJyenp6goKChoaGioqKkpKSlpaWmpqarq6usrKytra2urq6vr6+wsLCxsbGysrKzs7O1tbXBwcHCwsLFxcVD88dyAAAAKXRSTlMABQ4VGhwfJCQmLjE4OTpMTVFTU2BjZWp1gY2QlbCysrXIz9rs7vDx97MrGTQAAACNSURBVHja1chXFoIwEEDRsffeK/aOIhHEAkomlv2vyJGoR5fg+3sXvEq15pwJvLZS8CpczC5ti1DgZdLxOFjoGwfV2c6YoFy8DcoAOVNje/UkkeKOQmitN98ozu0/QkP7QbQJ/fGevvsgd4fdDABxMrE4mk/kfNSIwbt0vjJlKO71kHyfLLDSx9VIVPYApGc9qpWLk/0AAAAASUVORK5CYII='".format(
                        sum(self.state_dict.values())))
            print("---\nAWS owner tag: {0}|color=SteelBlue\n---".format(os.environ['USER']))
            state_bitbar_format_str="|color=DarkSlateGray"
        else:
            print("AWS owner tag: {0}".format(os.environ['USER']))
            if 'running' in self.state_dict:
                print ("Instances Running: {0}".format(self.state_dict['running']))
            else:
                print("0 Out of {0} Instances Running".format(sum(self.state_dict.values())))

         # max_state_width = max(map(len, state_dict))
        for k in self.state_dict.items():
            date_diff = str(datetime.datetime.now(pytz.utc) - self.time_dict[k[0]]).split(':')
            print("{0}: {1} instances / longest: {2} hrs {3} min{4}"
                  .format(k[0], k[1], date_diff[0], date_diff[1], state_bitbar_format_str))


def main():
    parser = MyParser()
    parser.add_argument("-t", "--term", help="output is formatted for terminal output, not bibar",
                        action="store_false")
    args = parser.parse_args()
    d = myAWS(args.term)
    d.doOutput()
    sys.exit(0)

if __name__ == '__main__':
    main()
