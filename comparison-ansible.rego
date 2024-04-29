# The following code is taken from https://github.com/Checkmarx/kics/blob/master/assets/libraries/ansible.rego

package generic.ansible

# Global variable with all tasks in input
tasks := TasksPerDocument

# Builds an object that stores all tasks for each document id
TasksPerDocument[id] = result {
	document := input.document[i]
	id := document.id
	result := getTasks(document)
}

# Function used to get all tasks from a document
getTasks(document) = result {
	document.playbooks[0].tasks
	result := [task |
		playbook := document.playbooks[0].tasks[_]
		task := getTasksFromBlocks(playbook)[_]
	]
} else = result {
	result := [task |
		playbook := document.playbooks[_]
		task := getTasksFromBlocks(playbook)[_]
	]
}

# Function used to get all nested tasks inside a block task ("block", "always", "rescue")
getTasksFromBlocks(playbook) = result {
	playbook.block
	result := [task |
		walk(playbook, [path, task])
		is_object(task)
		not task.block
		validPath(path)
	]
} else = [playbook] {
	true
}

# Validates the path of a nested element inside a block task to assure it's a task
validPath(path) {
	count(path) > 1
	validGroup(path[minus(count(path), 2)])
}

# Checks if a task is not an absent task
checkState(task) {
	state := object.get(task, "state", "undefined")
	state != "absent"
}


# The following code is taken from https://github.com/Checkmarx/kics/blob/master/assets/queries/ansible/aws/http_port_open_to_internet/query.rego
package Cx

import data.generic.ansible as ansLib

CxPolicy[result] {
	task := ansLib.tasks[id][t]
	modules := {"amazon.aws.ec2_group", "ec2_group"}
	ec2_group := task[modules[m]]
	ansLib.checkState(ec2_group)

	rule := ec2_group.rules[index]
	rule.cidr_ip == "0.0.0.0/0"
	ansLib.isPortInRule(rule, 80)

	result := {
		"documentId": id,
		"resourceType": modules[m],
		"resourceName": task.name,
		"searchKey": sprintf("name={{%s}}.{{%s}}.rules", [task.name, modules[m]]),
		"issueType": "IncorrectValue",
		"keyExpectedValue": sprintf("ec2_group.rules[%d] shouldn't open the http port (80)", [index]),
		"keyActualValue": sprintf("ec2_group.rules[%d] opens the http port (80)", [index]),
	}
}