# SERVER
receives either N (name - from messenger) or V (viewer) from client
receives msgs and transmits them to others
Message format: (len)(data)

# MESSENGER
Connects using name
usage: py ./messenger.py [name]
Sends messages using basic cmd prompt

# VIEWER
Connects using V
usage: py ./viewer.py
receives msgs (including information regarding new connections and recent disconnects)
