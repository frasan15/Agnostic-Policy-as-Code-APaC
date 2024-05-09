package example

import rego.v1

default allow := false # unless otherwise defined, allow is false

allow if { # allow is true if...
	count(violation) == 0 # there are zero violations.
}

violation contains server.name if { # a server is in the violation set if...
	server := input.servers[_]
	server.exposed_ports[_] == 22 # it contains the insecure "http" protocol.
}
