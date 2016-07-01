#!/usr/bin/python
#coding: utf-8 -*-
# Copyright 2016 Yanis Guenane <yguenane@redhat.com>
# Author: Yanis Guenane <yguenane@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ansible.module_utils.basic import *

try:
    import yaml
except ImportError:
    pyyaml_found = False
else:
    pyyaml_found = True


DOCUMENTATION = '''
---
module: swiftbackmeup_global
short_description: An Ansible module to manage swiftbackmeup globals in the configuration file
version_added: 2.2
options:
  state:
    required: false
    choices: ['present', 'absent']
    default: 'present'
    description: Wheter or not the mode should be present
  config:
    required: false
    description: Path of the swiftbackmeup config file, if not using the default
  name:
    required: true
    description: Name of the global parameter
  value:
    required: false
    description: Value of the global parameter
'''

EXAMPLES = '''
- name: Create a new global parameter
  swiftbackmeup_global: config=/etc/swiftbackmeup.conf
                        name=create_container
                        value=True

- name: Remove a global parameter
  swiftbackmeup_global: config=/etc/swiftbackmeup.conf
                        name=create_container
                        ensure=absent
'''

RETURN = '''
name:
  description: Name of the global parameter
  type: string
  sample: create_container
value:
  description: Value of the global parameter
  type: string
  sample: True
'''

class Parameter(object):

    def __init__(self, module):
        self.state = module.params['state']
        self.config = module.params['config']
        self.name = module.params['name']
        self.value = module.params['value']
        self.changed = True

    def write(self):
        try:
            swiftbackmeup_conf = yaml.load(open(self.config, 'r'))
        except:
            swiftbackmeup_conf = {}

        if swiftbackmeup_conf[self.name] == self.value:
            self.changed = False
        else:
            swiftbackmeup_conf[self.name] = self.value
            with open(self.config, 'w') as conf_file:
                conf_file.write(yaml.dump(swiftbackmeup_conf))


    def remove(self):
        swiftbackmeup_conf = yaml.load(open(self.config, 'r'))

        try:
            del swiftbackmeup_conf[self.name]
            with open(self.config, 'w') as conf_file:
                conf_file.write(yaml.dump(swiftbackmeup_conf))
        except KeyError:
            self.changed = False


    def dump(self):
    
        result = {
          'name': self.name,
          'value': self.value,
          'changed': self.changed,
        }

        return result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            config=dict(required=False, type='path', default='/etc/swiftbackmeup.conf'),
            name=dict(type='str'),
            value=dict(required=False, type='str'),
        ),
    )

    if not pyyaml_found:
        module.fail_json(msg='the python PyYAML module is required')

    path = module.params['config']
    base_dir = os.path.dirname(module.params['config'])

    if not os.path.isdir(base_dir):
        module.fail_json(name=base_dir, msg='The directory %s does not exist or the file is not a directory' % base_dir)

    parameter = Parameter(module)

    if parameter.state == 'present':
        parameter.write()
    else:
        parameter.remove()

    result = parameter.dump()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
