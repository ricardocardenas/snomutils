import sys
import cmd
from xmlrpclib import ServerProxy, Error
from getpass import getpass
import httplib
 
allSnomPhoneTypes = ["snom300", "snom370", "snom320", "snom360", "snomM3", "snomm9", "snomMP", "snomPA1", "snom820"]

snomTypeMap = {
    "23" : "snom360",
    "24" : "snom320",
    "25" : "snom300",
    "26" : "snom370",
    "27" : "snom320",
    "28" : "snom300",
    "29" : "snom360",
    "2A" : "snomM3",
    "2B" : "snom360",
    "2C" : "snom320",
    "2D" : "snom300",
    "2E" : "snom370",
    "2F" : "snom300",
    "30" : "snomm9",
    "31" : "snom320",
    "32" : "snomMP",
    "33" : "snomPA1",
    "34" : "snom300",
    "35" : "snom320",
    "36" : "snom300",
    "37" : "snom300",
    "38" : "snom320",
    "39" : "snom360",
    "3A" : "snom370",
    "3B" : "snom300",
    "3C" : "snom370",
    "3D" : "snom300",
    "40" : "snom820",
    "41" : "snom870",
    "45" : "snom821",
    "50" : "snom300",
    "51" : "snom320", # (Vodafone)
    "52" : "snom370", # (Vodafone)
    "53" : "snom821", # (Vodafone)
    "54" : "snom870", # (Vodafone)
    "55" : "snomMP", # (Vodafone)
    "56" : "snomm9", # (Vodafone)
}

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

  def disable(self):
    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''

def get_type(mac) :
    if mac[6:8] in snomTypeMap :
        return snomTypeMap[mac[6:8]]
    else :
        return "unknown"

def serviceLogin(username, password) :
  global server, host
  server = None
  scheme = "https"
  host = "provisioning.snom.com"
  port = "8083"
  path = "xmlrpc"
  server = ServerProxy(scheme + "://" + username + ":" + password + "@" + host + ":" + port + "/" + path + "/",
                       verbose=False, allow_none=True)
  try:
    server.network.echo("ping")
  except Error, err:
    print "  {2}Error{3}: {0} {1}".format(err.errcode, err.errmsg, bcolors.FAIL, bcolors.ENDC)
    return False
  return True

def get_redirection_target(mac, phonetype):
    global host
    conn = httplib.HTTPConnection(host)
    conn.request("GET", "/{0}/{0}.php?mac={1}".format(phonetype, mac))
    res = conn.getresponse()
    if res.status == 200:
        try:
	    responselines = res.read().splitlines()
            response1 = responselines[3]
            response2 = responselines[2]
            url = response1.split(': ')[1]
            return url
        except IndexError:
            try:
                url = response2.split('="')[1]
	        return url[:-4]
            except IndexError:
                print "  {0}Error{1} parsing URL information.".format(bcolors.FAIL, bcolors.ENDC)
                return None
    else:
        print "  {0}Error{1} fetching URL information".format(bcolors.FAIL, bcolors.ENDC)
        return None

class SnomRedirectCli(cmd.Cmd) :

    intro = "Welcome to SNOM Redirect CLI v0.6.\nThis is free software. Type 'help' or 'license' for more information."
    regUrl = ""
    completePhoneList = []

    def do_list(self, args):
        """  list phonetype [phonetype2...]\n  List MACs of phonetype which have been registered with Snom Redirect Service."""
        self.completePhoneList = []
        if args :
            listOfTypes = args.split()
        else :
            listOfTypes = allSnomPhoneTypes
        print "\n  {0:<12s} {1:8s} {2}".format("MAC address", "Type", "Registration URL")
        print "  {0}".format("-" * 80)
        for t in listOfTypes :
            phonelist = server.redirect.listPhones(t)
            phonelist.sort()
            self.completePhoneList.extend(phonelist)
            for m in phonelist :
                print "  {0:<12s} {1:8s} {2}".format(m, t, get_redirection_target(m, t))
        print "\n  CLI autocomplete updated. Total: {0}\n".format(len(self.completePhoneList))

    def do_seturl(self, args) :
        """  seturl address\n  Set registration URL to 'address'."""
        if args :
            print "  Setting registration URL to {0}".format(args)
            self.regUrl = args
        else :
            print "  {0}Error{1}: Please provide URL address.".format(bcolors.FAIL, bcolors.ENDC)

    def do_showurl(self, args) :
        """  showurl\n  Show registration URL currently in use."""
        if self.regUrl :
            print "  Registration URL is currently:", self.regUrl
        else :
            print "  Registration URL is not yet set."

    def do_copyurl(self, args) :
        """  copyurl mac\n  Copy the registration URL of the given MAC device (for use in more registrations)."""
        if not args :
            print "  {0}Error{1}: Please provide MAC to copy URL from.".format(bcolors.FAIL, bcolors.ENDC)
            return False
        m = args.upper()
        t = get_type(m)
        u = get_redirection_target(m, t)
        if u :
            self.regUrl = u
            print "  Registration URL set to", self.regUrl
        else :
            print "  {0}Error{1}: No value found. Registration URL not set.".format(bcolors.FAIL, bcolors.ENDC)

    def do_deregister(self, args) :
        """  deregister mac [mac2...]\n  Deregister phone from Snom Redirect Service."""
        if not args :
            print "{0}Error{1}: Please provide MACs to deregister.".format(bcolors.FAIL, bcolors.ENDC)
            return False
        print "  Deregistering {0}...".format(args),
        sys.stdout.flush()
        result = server.redirect.deregisterPhoneList(args.split())
        if result[0] : print "Ok."
        else : print "{0}Error{1}: {2}".format(bcolors.FAIL, bcolors.ENDC, result)

    def do_register(self, args) :
        """  register mac [mac2...]\n  Register phone at Snom Redirect Service."""
        if not args :
            print "  {0}Error{1}: Please provide MACs to register.".format(bcolors.FAIL, bcolors.ENDC)
            return False
        if not self.regUrl :
            print "  {0}Error{1}: Registration URL unset. Please use 'seturl' or 'copyurl' to set.".format(bcolors.FAIL, bcolors.ENDC)
            return False
        print "  Registering {0} at {1}...".format(args, self.regUrl),
        sys.stdout.flush()
        server.redirect.deregisterPhoneList(args.split())
        result = server.redirect.registerPhoneList(args.split(), self.regUrl)
        if result[0] :
            print "Ok."
        else :
            print "{0}Error{1}: {2}".format(bcolors.FAIL, bcolors.ENDC, result)
            return False

    def do_check(self, args) :
        """  check mac [mac2...]\n  Check if that phone has been registered by us."""
        if not args :
            print "  {0}Error{1}: Please provide MACs to check.".format(bcolors.FAIL, bcolors.ENDC)
            return False
        for mac in args.split() :
            m = mac.upper()
            print "  Checking", m, ":",
            sys.stdout.flush()
            result = server.redirect.checkPhone(m)
            if result[0] :
                t = get_type(m)
                u = get_redirection_target(m, t)
                print "Ok (type={0}, url={1}).".format(t, u)
            else :
                print "{0}Error{1}: {2}".format(bcolors.FAIL, bcolors.ENDC, result)

    def complete_list(self, text, line, begidx, endidx) :
        if not text :
            completions = allSnomPhoneTypes
        else :
            completions = [ f
                            for f in allSnomPhoneTypes
                            if f.startswith(text)
                          ]
        return completions

    def complete_deregister(self, text, line, begidx, endidx) :
        if not text :
            completions = self.completePhoneList
        else :
            completions = [ f for f in self.completePhoneList if f.startswith(text) ]
        return completions

    def complete_check(self, text, line, begidx, endidx) :
        if not text :
            completions = self.completePhoneList
        else :
            completions = [ f for f in self.completePhoneList if f.startswith(text) ]
        return completions

    def complete_copyurl(self, text, line, begidx, endidx) :
        if not text :
            completions = self.completePhoneList
        else :
            completions = [ f for f in self.completePhoneList if f.startswith(text) ]
        return completions

    def do_license(self, args) :
        """  Show license."""
        print """Copyright (C) 2012-2013 rcardenas@alum.mit.edu

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

    def do_quit(self, args) :
        """  quit: End Snom CLI"""
        print "Goodbye."
        return True

    def do_exit(self, args) :
        """  exit: End Snom CLI"""
        print "Goodbye."
        return True

    def do_EOF(self, args) :
        print "  Goodbye."
        return True

    def postloop(self) :
        print

    def preloop(self) :
        username = raw_input("Username: ")
        password = getpass("Password: ")

        if serviceLogin(username, password) :
            print
            self.prompt = username + "@" + host + "> "
        else :
            quit()

if __name__ == '__main__' :
    SnomRedirectCli().cmdloop()
