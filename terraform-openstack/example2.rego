# This Rego file checks if any server exposes port 80 and it is connected to Internet (in this implementation it just means that it has got a floating ip)

package example

import rego.v1

default allow := false                              # unless otherwise defined, allow is false

allow if {                                          # allow is true if...
    count(violation) == 0                           # there are zero violations.
}

violation contains server.id if {                   # a server is in the violation set if...
    some server
    public_servers[server]                          # it exists in the 'public_servers' set and...
    server.exposed_ports[_] == 80 # it contains the insecure "http" protocol.
}

public_servers contains server if {                 # a server exists in the 'public_servers' set if...
    some i, j
    server := input.servers[_]                      # it exists in the input.servers collection and...
    input.servers[i].network_interfaces[_] == input.network_interfaces[j].name  # the port references a network in the input.networks collection and...
    input.network_interfaces[j].is_public                        # the network is public.
}