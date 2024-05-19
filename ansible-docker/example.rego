# This Rego file checks if any server exposes port 80

package example

import rego.v1

default allow := false # unless otherwise defined, allow is false


# possible TODO: if allow is false for exposed port 22 = true then you could print a message saying "port 22 must not be exposed"
# instead if allow is false for another policy you could generate another error message

allow if { # allow is true if...
        count(violation) == 0 # there are zero violations.
}

violation contains server.name if { # a server is in the violation set if...
        server := input.servers[_]
        server.exposed_ports[_] == 22 # it contains the insecure "http" protocol.
}