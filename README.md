snomutils
=========

snomredirectcli.sh
-----------

Snom IP phones have a great feature called auto-provisioning. This means that, on startup, the phones consult several locations in the 
hope of receiving their configuration. The first place they consult is Snom's Redirect Service, which will redirect the phone to your 
preferred location. In order to use this feature, you must have previously requested web service credentials from Snom. snomredirectcli.py 
is a Line Interface which allows you to register and deregister phones with Snom. To use, type

    snomredirectcli.sh

Enter your Snom provisioning web service credentials (you must request these from Snom) and type help.

gensnomxml.sh
----------

The configuration for Snom IP phones can live in XML files. gensnomxml.sh is an effort to automate the creation of those XML files. To 
use, just execute

    gensnomxml.sh

to get more information.
