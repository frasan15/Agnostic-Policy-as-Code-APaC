package example

import rego.v1

default allow := false # unless otherwise defined, allow is false

allow if { # allow is true if...
	count(violation) == 0 # there are zero violations.
}

violation contains server.id if { # a server is in the violation set if...
	server := input.servers[_]
	server.protocols[_] == "http" # it contains the insecure "http" protocol.
}

violation contains server.id if { # a server is in the violation set if...
	server := input.servers[_] # it exists in the input.servers collection and...
	server.protocols[_] == "telnet" # it contains the "telnet" protocol.
}