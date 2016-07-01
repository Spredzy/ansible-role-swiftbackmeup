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


_PROPERTIES = ['name', 'type', 'os_username', 'os_password', 'os_tenant_name',
               'os_auth_url', 'store_type', 'create_container',
               'purge_container', 'swift_container', 'swift_pseudo_folder',
               'output_directory', 'clean_local_copy', 'backup_filename',
               'backup_filename_prefix', 'backup_filename_suffix',
               'subscriptions', 'path', 'branches']


DOCUMENTATION = '''
---
module: swiftbackmeup_git
short_description: An Ansible module to manage swiftbackmeup git items in the configuration file
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
  path:
    required: true
    description: Path to the git repository on the local filesystem
  branches:
    required: false
    description: Branches that should be backedup by swiftbackmeup
'''

EXAMPLES = '''
- name: Create a git backup item (with all branches)
  swiftbackmeup_git: config=/etc/swiftbackmeup.conf
                     name=git_superproject
                     path=/srv/git/git_superproject
                     branches=all

- name: Create a git backup item (with only master branch)
  swiftbackmeup_git: config=/etc/swiftbackmeup.conf
                     name=git_superproject
                     path=/srv/git/git_superproject
                     branches=master

- name: Remove a git backup item
  swiftbackmeup_git: config=/etc/swiftbackmeup.conf
                     name=git_superproject
                     state=absent
'''

RETURN = '''
name:
  description: Name of the git project
  type: string
  sample: git_superproject
path:
  description: Path to the git project
  type: string
  sample: /srv/git/git_superproject
branches:
  description: Branches to backup from the git project
  type: string
  sample: master
'''

class Item(object):

    def __init__(self, module):
        self.state = module.params['state']
        self.config = module.params['config']
        self.name = module.params['name']
        self.type = 'git'
        self.changed = True

        self.os_username = module.params['os_username']
        self.os_password = module.params['os_password']
        self.os_tenant_name = module.params['os_tenant_name']
        self.os_auth_url = module.params['os_auth_url']
        self.store_type = module.params['store_type']
        self.create_container = module.params['create_container']
        self.purge_container = module.params['purge_container']
        self.swift_container = module.params['swift_container']
        self.swift_pseudo_folder = module.params['swift_pseudo_folder']

        self.output_directory = module.params['output_directory']
        self.clean_local_copy = module.params['clean_local_copy']
        self.backup_filename = module.params['backup_filename']
        self.backup_filename_prefix = module.params['backup_filename_prefix']
        self.backup_filename_suffix = module.params['backup_filename_suffix']
        self.subscriptions = module.params['subscriptions']

        self.path = module.params['path']
        self.branches = module.params['branches']


    def write(self):
        l_backup = {}
        for prop in _PROPERTIES:
            if getattr(self, prop):
                l_backup[prop] = getattr(self, prop)

        try:
            swiftbackmeup_conf = yaml.load(open(self.config, 'r'))
        except:
            swiftbackmeup_conf = {}

        backups = []
        c_backup = None
        for backup in swiftbackmeup_conf['backups']:
            if backup['name'] != self.name:
                backups.append(backup)
            else:
                c_backup = backup

        if c_backup == l_backup: 
            self.changed = False
        else:
            backups.append(l_backup)
            swiftbackmeup_conf['backups'] = backups
            with open(self.config, 'w') as conf_file:
                conf_file.write(yaml.dump(swiftbackmeup_conf))


    def remove(self):
        try:
            swiftbackmeup_conf = yaml.load(open(self.config, 'r'))
        except:
            swiftbackmeup_conf = {}

        backups = None
        if 'backups' in swiftbackmeup_conf:
            backups = [backup for backup in swiftbackmeup_conf['backups'] if backup['name'] != self.name]
       
        if 'backups' not in swiftbackmeup_conf or backups == swiftbackmeup_conf['backups']:
            self.changed = False
        else:
            swiftbackmeup_conf['backups'] = backups
            with open(self.config, 'w') as conf_file:
                conf_file.write(yaml.dump(swiftbackmeup_conf))


    def dump(self):
    
        result = {
          'name': self.name,
          'changed': self.changed,
        }

        return result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            config=dict(required=False, type='path', default='/etc/swiftbackmeup.conf'),
            name=dict(type='str'),

            os_username=dict(required=False, type='str'),
            os_password=dict(required=False, type='str'),
            os_tenant_name=dict(required=False, type='str'),
            os_auth_url=dict(required=False, type='str'),
            store_type=dict(required=False, type='str'),
            create_container=dict(required=False, type='str'),
            purge_container=dict(required=False, type='str'),
            swift_container=dict(required=False, type='str'),
            swift_pseudo_folder=dict(required=False, type='str'),

            output_directory=dict(required=False, type='str'),
            clean_local_copy=dict(required=False, type='str'),
            backup_filename=dict(required=False, type='str'),
            backup_filename_prefix=dict(required=False, type='str'),
            backup_filename_suffix=dict(required=False, type='str'),
            subscriptions=dict(required=False, type='str'),

            path=dict(type='path'),
            branches=dict(required=False, type='str'),
        ),
    )

    if not pyyaml_found:
        module.fail_json(msg='the python PyYAML module is required')

    path = module.params['config']
    base_dir = os.path.dirname(module.params['config'])

    if not os.path.isdir(base_dir):
        module.fail_json(name=base_dir, msg='The directory %s does not exist or the file is not a directory' % base_dir)

    item = Item(module)

    if item.state == 'present':
        item.write()
    else:
        item.remove()

    result =item.dump()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
