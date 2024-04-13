# For Game2
{var} means that is is a variable
## CLIENT TO SERVER GRAMMAR
	request ::= request_line
	request_line ::= start | options id
	start ::= CONNECT
	id ::= {UUID}
	options ::= GET get_options | STORE data | KMS 
	get_options ::= POS | FOREIGN_PLAYERS
	data ::= DATA CONTENT_LENGTH {DATA}

## SERVER TO CLIENT GRAMMAR
	response ::= response_line
	response_line ::= KYS | options
	options ::= data | STORE data | DEL id
	id ::= {UUID}
	data ::= DATA CONTENT_LENGTH {ACTUAL_DATA}
