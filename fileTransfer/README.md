```plaintext
Sender                 Receiver
                         <- REQF
ACK ->
INFO ->
                         <- ACK
                         <- REQB
SEND ->
                         <- BYE
BYE ->
```

Payload (actual data being transfered)

REQF - Payload contains utf-8 encoded string name of the file
ACK (by server) - same payload that was in the reqf if file exists, empty otherwise.


INFO
16 bytes (128 bit) md5 checksum of the file
4 bytes (unsigned int) file size
4 bytes max block size (CHUNK SIZE)
4 bytes - total number of blocks transfered

ACK (empty payload should be sent by recvier)

REQB payload is unsigned int the block number that is being requested by the receiver

SEND - payload a block who's number corresponds to the one requested in reqb

`MAX_BLOCK_SZ` is 2048
and `CHUNK_SZ` is 4096

the max payload size should always be less than `CHUNK_SZ` here for this to work nicely.

example usage: 
python3 server.py
python3 client.py awesomeface.png mydirec/awesomeface.png

This is kind of a trashier version of Benjamin N. Summerton's tutorial on udp file transfer

