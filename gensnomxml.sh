#!/bin/bash

# defaults
progname="$(basename $0)"
macprefix="000413"
realm="asterisk"
password="888aaa"
addlxml=""
userhost=""
identities=""
numidentity=0

usage="$progname: Create SNOM provisioning XML file.

Usage: $progname [-x <macprefix>] [-r <realm>] [-p <password>] [-i <additional XML text>]
                    [-g <user_host_ip_or_name>] <macsuffix> <extension> [<extension>...]
  -p: SIP password
  -x: macprefix (default: 000413)
  -r: realm of SIP server (default: asterisk)
  -g: user_host (Snom parameter, SIP registration host)
  -a: include additional XML text in config file phone settings
  -h: print help and exit

Examples: \"$progname -x 000412 -r pbxrealm -p 84aa83 -g 190.187.43.2 3BFA37 301\" generates 0004123BFA37.xml
          \"$progname -a '<dhcp perm=\"\">on</dhcp>' 3EF23A 7004 7010\" generates 00041333EF23A.xml"

while getopts :x:r:p:a:g:h flag
  do
    case $flag in
      p) password="$OPTARG";;
      x) macprefix="$OPTARG";;
      r) realm="$OPTARG";;
      g) userhost="$OPTARG";;
      a) addlxml="$OPTARG
";;
      h) echo "$usage"; exit;;
      \?) echo "Invalid option -$OPTARG"; echo "$usage"; exit;;
    esac
  done
shift $(( OPTIND - 1 ))  # shift past the last flag or argument

if [ $# -lt 2 ]
then
  echo "$usage"
  exit
fi

mac=$1; xmlfile=`echo -n $macprefix$mac | tr '[a-z]' '[A-Z]'`.xml
echo -n "File $xmlfile. "
shift

while [ $# -gt 0 ]
do
  numidentity=$(( numidentity + 1 ))
  extension=$1
  hash=`echo -n "$extension:$realm:$password" | md5sum | awk '{print $1}'`
  if [ $userhost ]; then
    identities="$identities  <user_host     idx=\"$numidentity\" perm=\"\">$userhost</user_host>
"
  fi
  identities="$identities\
  <user_realname idx=\"$numidentity\" perm=\"\">$extension</user_realname>
  <user_name     idx=\"$numidentity\" perm=\"\">$extension</user_name>
  <user_hash     idx=\"$numidentity\" perm=\"\">$hash</user_hash>
"
  echo -n "Identity $numidentity extension $extension hash $extension:$realm:$password. "
  shift
done
echo

#echo "Removing file $xmlfile..."
rm -rf $xmlfile

#echo "Creating file $xmlfile..."
cat > $xmlfile << _EOF_
<?xml version="1.0" encoding="utf-8"?>
<settings>
 <phone-settings e="2">
$identities$addlxml </phone-settings>
</settings>
_EOF_
