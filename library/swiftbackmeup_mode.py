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
module: swiftbackmeup_mode
short_description: An Ansible module to manage swiftbackmeup modes
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
    description: Name of the mode
  retention:
    required: false
    description: Retention value for the backup matching this mode
  unit:
    required: false
    choices: ['days', 'item']
    default: 'days'
    description: Unit in which to express the retention number
  pattern:
    required: true
    description: Pattern that will be evaluated by datetime.format() to name the generated backup
'''

EXAMPLES = '''
- name: Create a new mode
  swiftbackmeup_mode: config=/etc/swiftbackmeup.conf
                      name=daily
                      retention=7
                      unit=days 
                      pattern=daily_%Y%m%d

- name: Remove a mode
  swiftbackmeup_mode: config=/etc/swiftbackmeup.conf
                      name=daily
                      ensure=absent
'''

RETURN = '''
name:
  description: Name of the mode
  type: string
  sample: daily
retention:
  description: Retention value for the backup matching this mode
  type: integer
  sample: 7
unit:
  description: Unit in which to express the retention number
  type: string
  sample: days
pattern:
  description: Pattern that will be evaluated by datetime.format() to name the generated backup
  type: string
  sample: daily_%Y%m%d
'''

class Mode(object):

    def __init__(self, module):
        self.state = module.params['state']
        self.config = module.params['config']
        self.name = module.params['name']
        self.retention = module.params['retention']
        self.unit = module.params['unit']
        self.pattern = module.params['pattern']
        self.changed = True

    def write(self):
        try:
            swiftbackmeup_conf = yaml.load(open(self.config, 'r'))
        except:
            swiftbackmeup_conf = {}

        try:
            modes = swiftbackmeup_conf['modes']
        except KeyError:
            modes = {}

        modes[self.name] = {}
        for option in ['retention', 'unit', 'pattern']:
            if getattr(self, option):
                modes[self.name][option] = getattr(self, option)

        # TODO (spredzy): If modes == swiftbackmeup_conf['modes']
        # set self.changed to False
        swiftbackmeup_conf['modes'] = modes

        with open(self.config, 'w') as conf_file:
            conf_file.write(yaml.dump(swiftbackmeup_conf))


    def remove(self):
        swiftbackmeup_conf = yaml.load(open(self.config, 'r'))

        try:
            del swiftbackmeup_conf['modes'][self.name]
            with open(self.config, 'w') as conf_file:
                conf_file.write(yaml.dump(swiftbackmeup_conf))
        except KeyError:
            self.changed = False


    def dump(self):
    
        result = {
          'name': self.name,
          'pattern': self.pattern,
          'changed': self.changed,
        }

        if self.retention:
            result['retention'] = self.retention

        if self.unit:
            result['unit'] = self.unit

        return result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            config=dict(required=False, type='path', default='/etc/swiftbackmeup.conf'),
            name=dict(type='str'),
            retention=dict(required=False, type='int'),
            unit=dict(required=False, type='str', choices=['days', 'item'], default='days'),
            pattern=dict(type='str'),
        ),
    )

    if not pyyaml_found:
        module.fail_json(msg='the python PyYAML module is required')

    path = module.params['config']
    base_dir = os.path.dirname(module.params['config'])

    if not os.path.isdir(base_dir):
        module.fail_json(name=base_dir, msg='The directory %s does not exist or the file is not a directory' % base_dir)

    mode = Mode(module)

    if mode.state == 'present':
        mode.write()
    else:
        mode.remove()

    result = mode.dump()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
