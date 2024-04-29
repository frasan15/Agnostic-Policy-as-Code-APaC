# The following code is from https://github.com/Checkmarx/kics/blob/master/assets/libraries/terraform.rego
package generic.terraform

import data.generic.common as common_lib

# This rule checks if the CIDR block in the given rule allows access from the entire internet (0.0.0.0/0). 
# If the rule is an array of CIDR blocks (rule.cidr_blocks), it checks if any of the CIDR blocks match "0.0.0.0/0". 
# If the rule is a single CIDR block (rule.cidr_block), it checks if the CIDR block matches "0.0.0.0/0". 
# This rule is used internally by portOpenToInternet(rule, port) to verify if the rule allows access from the 
# entire internet.

check_cidr(rule) {
	rule.cidr_blocks[_] == "0.0.0.0/0"
} else {
	rule.cidr_block == "0.0.0.0/0"
}

# Checks if a TCP port is open in a rule
portOpenToInternet(rule, port) {
	check_cidr(rule)
	rule.protocol == "tcp"
	containsPort(rule, port)
}

# The following code is taken from https://github.com/Checkmarx/kics/blob/master/assets/queries/terraform/aws/http_port_open/query.rego

package Cx

import data.generic.terraform as tf_lib

CxPolicy[result] {
	resource := input.document[i].resource.aws_security_group[name]

	tf_lib.portOpenToInternet(resource.ingress, 80)

	result := {
		"documentId": input.document[i].id,
		"resourceType": "aws_security_group",
		"resourceName": tf_lib.get_resource_name(resource, name),
		"searchKey": sprintf("aws_security_group[%s]", [name]),
		"issueType": "IncorrectValue",
		"keyExpectedValue": "aws_security_group.ingress shouldn't open the HTTP port (80)",
		"keyActualValue": "aws_security_group.ingress opens the HTTP port (80)",
	}
}