# For Game2
{var} means that it is a variable
## CLIENT TO SERVER GRAMMAR
	request ::= request_line
	request_line ::= start | options id | EAT
	start ::= CONNECT
	id ::= DATA ID_LEN {UUID}
	options ::= GET get_options | STORE data(obj) | KMS | UPDATE data(direction) | VERIFY data(position)
	get_options ::= POS | FOREIGN_PLAYERS
	data(x) ::= DATA CONTENT_LENGTH {x}

## SERVER TO CLIENT GRAMMAR
	start ::= response_line | request_line
 	request_line ::= req_options id
	response_line ::= resp_options
	req_options ::= DEL | update | KYS | ACPT | RJCT | food_update
	resp_options ::= KYS | data
	update ::= UPDATE data(position) data(direction)
	id ::= DATA ID_LEN {UUID}
 	foreigners ::= FOREIGN_PLAYERS id data
	food_update ::= FOOD_UPDATE data(foodPos)
	data(x) ::= DATA CONTENT_LENGTH {x}


TO DO:
Client maintains a queue of the positions that it has been on and sends those to the server
to get them checked one by one, the server checks if the new position is a good position
based on the previous position and the direction and sends the client ACPT or RJCT.
In case of RJCT the queue is emptied and the starting position is the one given by the server.
This way the client can move continuously.

Synchornizing client two's movement in client one:
when client X changes its direction it sends UPDATE to the server to change its direction, the position
verification takes place here too. The server then sends this position and direction to the rest of the clients 
so that they can change client X's pos and dir to the one received.