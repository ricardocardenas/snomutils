import sys
import cmd
from xmlrpclib import ServerProxy, Error
from getpass import getpass
import httplib
 
type_map = {
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

server = None

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

def get_type(mac):
    if mac[6:8] in type_map:
        return type_map[mac[6:8]]
    else:
        print "  Unknown device type (maybe not a snom MAC?)"
        return None

def snomLogin(snomUsername, snomPassword) :
  snomURIScheme = "https://"
  snomService = "provisioning.snom.com:8083/xmlrpc/"
  global server
  server = ServerProxy(snomURIScheme + snomUsername + ":" + snomPassword + "@" + snomService, verbose=False, allow_none=True)
  try:
    server.network.echo("ping")
  except Error, err:
    print "  {2}Error{3}: {0} {1}".format(err.errcode, err.errmsg, bcolors.FAIL, bcolors.ENDC)
    return False
  return True

def get_redirection_target(mac):
    conn = httplib.HTTPConnection("provisioning.snom.com")
    conn.request("GET", "/{0}/{0}.php?mac={1}".format(get_type(mac), mac))
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

  intro = "Welcome to SNOM Redirect CLI v0.5.\nThis is free software. Type 'help' or 'license' for more information."
  regUrl = ""
  completePhoneList = []
  snomPhoneTypes = ["snom300", "snom370", "snom320", "snom360",
                  "snomM3", "snomm9", "snomMP", "snomPA1", "snom820"]

  def snomList(self, listOfTypes):
    self.completePhoneList = []
    if listOfTypes[0] == "all" :
      listOfTypes = self.snomPhoneTypes
    print "\n  {0:<12s} {1:8s} {2}".format("MAC address", "Type", "Registration URL")
    print "  {0}".format("-" * 80)
    for phonetype in listOfTypes :
      phonelist = server.redirect.listPhones(phonetype)
      phonelist.sort()
      for mac in phonelist :
        print "  {0:<12s} {1:8s} {2}".format(mac, phonetype, get_redirection_target(mac))
      self.completePhoneList.extend(phonelist)
    print "\n  CLI autocomplete updated. Total: {0}\n".format(len(self.completePhoneList))

  def do_list(self, phoneTypes) :
    """  list phonetype [phonetype2...]\n  List MACs of phonetype which have been registered with Snom Redirect Service."""
    if phoneTypes :
      self.snomList(phoneTypes.split())
    else :
      print "  {0}Error{1}: Must provide phonetypes (e.g. 'list snom300 snom320')".format(bcolors.FAIL, bcolors.ENDC)

  def do_seturl(self, line) :
    """  seturl address\n  Set registration URL to 'address'."""
    if line :
      print "  Setting registration URL to {0}".format(line)
      self.regUrl = line
    else :
      print "  {0}Error{1}: Must provide URL address.".format(bcolors.FAIL, bcolors.ENDC)

  def do_showurl(self, line) :
    """  showurl\n  Show registration URL currently in use."""
    if self.regUrl :
      print "  Registration URL is currently:", self.regUrl
    else :
      print "  Registration URL is not yet set."

  def do_copyurl(self, MAC) :
    """  copyurl mac\n  Copy the registration URL of the given MAC device (for use in more registrations)."""
    if MAC :
      x = get_redirection_target(MAC.upper())
      if x :
        self.regUrl = x
        print "  Registration URL set to", self.regUrl
      else :
        print "  {0}Error{1}: No value found. Registration URL not set.".format(bcolors.FAIL, bcolors.ENDC)
    else : print "  {0}Error{1}: Must provide MAC.".format(bcolors.FAIL, bcolors.ENDC)

  def do_deregister(self, MACs) :
    """  deregister mac [mac2...]\n  Deregister phone from Snom Redirect Service."""
    if MACs :
      print "  Deregistering {0}...".format(MACs),
      sys.stdout.flush()
      result = server.redirect.deregisterPhoneList(MACs.split())
      if result[0] : print "Ok."
      else : print "{0}Error{1}: {2}".format(bcolors.FAIL, bcolors.ENDC, result)
    else : print "{0}Error{1}: Must provide MACs to deregister.".format(bcolors.FAIL, bcolors.ENDC)

  def do_register(self, MACs) :
    """  register mac [mac2...]\n  Register phone at Snom Redirect Service."""
    if not MACs :
      print "  {0}Error{1}: Must provide MACs to register.".format(bcolors.FAIL, bcolors.ENDC)
      return False
    if not self.regUrl :
      print "  {0}Error{1}: Registration URL is empty. Please use 'seturl' or 'copyurl' first.".format(bcolors.FAIL, bcolors.ENDC)
      return False
    print "  Registering {0} at {1}...".format(MACs, self.regUrl),
    sys.stdout.flush()
    server.redirect.deregisterPhoneList(MACs.split())
    result = server.redirect.registerPhoneList(MACs.split(), self.regUrl)
    if result[0] :
      print "Ok."
    else :
      print "{0}Error{1}: {2}".format(bcolors.FAIL, bcolors.ENDC, result)

  def do_check(self, MACs) :
    """  check mac [mac2...]\n  Check if that phone has been registered by us."""
    if MACs :
      for mac in MACs.split() :
        print "  Checking", mac, ":",
        sys.stdout.flush()
        result = server.redirect.checkPhone(mac)
        if result[0] : print "Ok (type={0}, url={1}).".format(get_type(mac.upper()),get_redirection_target(mac.upper()))
        else : print "{0}Error{1}: {2}".format(bcolors.FAIL, bcolors.ENDC, result)
    else : print "  {0}Error{1}: Please provide MACs to check.".format(bcolors.FAIL, bcolors.ENDC)

  def complete_list(self, text, line, begidx, endidx) :
    if not text :
      completions = self.snomPhoneTypes
    else :
      completions = [ f
                      for f in self.snomPhoneTypes
                      if f.startswith(text)
                    ]
    return completions

  def complete_deregister(self, text, line, begidx, endidx) :
    if not text :
      completions = self.completePhoneList
    else :
      completions = [ f
                      for f in self.completePhoneList
                      if f.startswith(text)
                    ]
    return completions

  def complete_check(self, text, line, begidx, endidx) :
    if not text :
      completions = self.completePhoneList
    else :
      completions = [ f
                      for f in self.completePhoneList
                      if f.startswith(text)
                    ]
    return completions

  def complete_copyurl(self, text, line, begidx, endidx) :
    if not text :
      completions = self.completePhoneList
    else :
      completions = [ f
                      for f in self.completePhoneList
                      if f.startswith(text)
                    ]
    return completions

  def do_license(self, line) :
    """  Show license."""
    print """Copyright (C) 2012 rcardenas@alum.mit.edu

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

  def do_quit(self, line) :
    """  quit: End Snom CLI"""
    print "Goodbye."
    return True

  def do_exit(self, line) :
    """  exit: End Snom CLI"""
    print "Goodbye."
    return True

  def do_EOF(self, line) :
    print "  Goodbye."
    return True

  def postloop(self) :
    print

  def preloop(self) :
    snomUsername = raw_input("Username: ")
    snomPassword = getpass("Password: ")

    if snomLogin(snomUsername, snomPassword):
      print
      self.prompt = snomUsername + "@snom> "
    else:
      quit()

if __name__ == '__main__' :
    SnomRedirectCli().cmdloop()

