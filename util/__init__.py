# -*- coding: utf-8 -*-
from util.hook import *

def cmd2str(cmd):
    return ";".join( [ ("%s=%.2f" if name == "price" else "%s=%s") % ( name.upper(), cmd[name] ) for name in cmd ] )

