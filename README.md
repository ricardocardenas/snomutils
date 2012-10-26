snomutils
=========

snormredirectcli.py
-----------

Snom IP phones have a great feature called auto-provisioning. This means that, on startup, the phones consult several locations in the 
hope of receiving their configuration. The first place they consult is a Snom auto-provisioning server itself, which will redirect them to 
the location where you store the configuration for the phones. In order to use this feature, you must register your phones with a Snom web 
service. snomredirectcli.py is a Command Line Interface which allows you to register and deregister phones with Snom. To use, type

    python snomredirectcli.py

Enter your Snom provisioning web service credentials (you must request these from Snom) and type help.

gensnomxml.sh
----------

The configuration for Snom IP phones can live in XML files. gensnomxml.sh is an effort to automate the creation of those XML files. To 
use, just execute

    gensnomxml.sh

to get more information.
