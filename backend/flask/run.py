from www import app

HOST = 'localhost'   # This restricts incoming calls to the local machine
#HOST = '0.0.0.0'     # This allows incoming calls from outside the machine (Windows will ask for Firewall permission)
PORT = 7882          # Arbitrary port (epoch accessible from outside)

import os
debug=os.environ.get("FLASK_DEBUG", False)  # Better default choice than True

if debug:
  print "Debugging is on"

app.run(host=HOST, port=PORT, debug=debug, )
