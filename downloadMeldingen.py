#-------------------------------------------------------------------------------
# Name: downloadMeldingen.py
# Purpose:
#
# Author(s):  Antoon Uitjdehaag
# Created: 122-01-2018
# Version: 1.0
#-------------------------------------------------------------------------------
from Zaaksysteem import Zaaksysteem
import config as cnf

Zs = Zaaksysteem (cnf.URL, cnf.API_Interface_Id, cnf.API_Key)

# define start and enddate
# these parameters are optional
startdate = '"2014-01-01"'
enddate =  '"2014-12-31"'

Zs.queryAll('Melding woon of leefomgeving',100,startdate,enddate)

# Dowl
#Zs.queryAll('Melding woon of leefomgeving',100)