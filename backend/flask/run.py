from www import app

HOST = 'localhost'   # This restricts incoming calls to the local machine
#HOST = '0.0.0.0'     # This allows incoming calls from outside the machine (Windows will ask for Firewall permission)
PORT = 7882          # Arbitrary port (epoch accessible from outside)

#import platform
#hostname = platform.uname()[1]

#print "HOSTNAME = %s" % hostname

import os
# Better default choice than True
debug=os.environ.get("FLASK_DEBUG", False)

#if hostname.endswith('herald') or hostname.endswith('localhost') :
#    debug=True

## http://blog.rootsmith.ca/uncategorized/request-server-or-hostname-must-match-flasks-server_name-to-route-successfully/
#import os
#if 'SERVER_NAME' in os.environ:
#    print os.environ['SERVER_NAME']

if debug:
  print "Debugging is on"

app.run(host=HOST, port=PORT, debug=debug, )
