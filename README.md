# For Game2
{var} means that it is a variable
## CLIENT TO SERVER GRAMMAR
	request ::= request_line
	request_line ::= start | options id
	start ::= CONNECT
	id ::= DATA ID_LEN {UUID}
	options ::= GET get_options | STORE data | KMS 
	get_options ::= POS | FOREIGN_PLAYERS
	data ::= DATA CONTENT_LENGTH {DATA}

## SERVER TO CLIENT GRAMMAR
	start ::= response_line | request_line
 	request_line ::= DEL id
	response_line ::= KYS | options
	options ::= data | STORE data | foreigners
	id ::= DATA ID_LEN {UUID}
 	foreigners ::= FOREIGN_PLAYERS id data
	data ::= DATA CONTENT_LENGTH {DATA}
