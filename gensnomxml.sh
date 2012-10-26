#!/bin/bash

# defaults
macprefix=000413
realm=asterisk
password=888aaa

usage="
$(basename $0): Create SNOM provisioning XML file.

Usage: $(basename $0) [-x <macprefix>] [-r <realm>] [-p <password>] <mac> <extension>
  -x: prefix prepended to MAC address (default: 000413)
  -r: realm of SIP server (default: asterisk)
  -p: SIP password

Example: \"$(basename $0) -x 000412 -r pbxrealm -p 84aa83 3BFA37 301\" will generate 0004B23BFA37.xml
"

while getopts x:r:p:h flag
  do
    case $flag in
      x)
        macprefix=$OPTARG
        ;;
      r)
        realm=$OPTARG
        ;;
      p)
        password=$OPTARG
        ;;
      h)
        echo $usage
        exit
        ;;
    esac
  done
shift $(( OPTIND - 1 ))  # shift past the last flag or argument

if [ $# != 2 ]; then
  echo $usage
  exit
fi

mac=$1
extension=$2

xmlfile=`echo -n $macprefix$mac | tr '[a-z]' '[A-Z]'`.xml

echo -n "File $xmlfile, extension $extension, password hash $extension:$realm:$password..."
hash=`echo -n "$extension:$realm:$password" | openssl dgst -md5 | awk '{print $1}'`

#echo "Removing file $xmlfile..."
rm -rf $xmlfile

#echo "Creating file $xmlfile with extension $extension..."
cat > $xmlfile << _EOF_
<?xml version="1.0" encoding="utf-8"?>
<settings>
<phone-settings e="2">
<phone_name perm="RW"></phone_name>
<user_realname idx="1" perm="">$extension</user_realname>
<user_name idx="1" perm="">$extension</user_name>
<user_hash idx="1" perm="">$hash</user_hash>
</phone-settings>
</settings>
_EOF_

echo "Done."
