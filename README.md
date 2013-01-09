snomutils
=========

snomredirectcli.sh
-----------

Snom IP phones have a great feature called auto-provisioning. This means that, on startup, the phones consult several 
locations in the hope of receiving their configuration. The first place they consult is Snom's Redirect Service, an 
XML-RPC web service which will then redirect the phone to the location where you keep those configuration files. 
snomredirectcli.sh calls the Python program snomredirectcli.py, a Command Line Interface (CLI) which allows you to 
register and deregister phones with Snom's XML-RPC redirection web service. To use, type

    snomredirectcli.sh

In order to use this utility, you must have previously requested web service credentials from Snom. See 
http://wiki.snom.com/Features/Auto_Provisioning/Redirection for more information on Snom Auto Provisioning.

gensnomxml.sh
----------

The configuration for Snom IP phones can live in XML files. gensnomxml.sh is an effort to automate the creation of 
those XML files. To use, just execute

    gensnomxml.sh

to get more information.
