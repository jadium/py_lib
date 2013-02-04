#!/usr/bin/python
from optparse import OptionParser
import time, os, random, sys

parser = OptionParser()
parser.add_option("-c", "--counter", dest="counter", default=False,  help="specify counter")
parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true",  help="specify display of debug statements")
parser.add_option("-i", "--icmp4", dest="p4", default=False, help="specify path to p4 executable")
parser.add_option("-p", "--port", dest="p4_port", default=False, help="specify p4 port to icmbroker ip:port")
parser.add_option("-u", "--user", dest="p4_user", default="icmAdmin", help="specify p4 user")
opt = parser.parse_args()[0]
try:
	if not(opt.counter and opt.p4_port and opt.icmp4):
		parser.print_help()
		sys.exit(1)
	debug = " "
	if not opt.debug:
		debug = " > /dev/null 2>&1 "
	for i in range(3):
		cmd = "%s -p %s -u %s counter %s %s %s "%(opt.icmp4, opt.p4_port, opt.p4_user, opt.counter, random.randint(0,(2**32)-1), debug)
		if opt.debug:
			print cmd
		os.system(cmd)
		time.sleep(15)
	sys.exit(0)
except:
	sys.exit(1)

