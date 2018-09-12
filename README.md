# Ansible Role: swiftbackmeup

Installs and configures `swiftbackmeup` on a server.


## Requirements

No special requirements; note that this role requires root access, so either run it in a playbook with a global `become: yes`, or invoke the role in your playbook like:

    - hosts: database
      roles:
        - role: Spredzy.swiftbackmeup
          become: yes

## Role Variables

This is the list of role variables. Examples are found below.

  * `swiftbackmeup_crons`
  * `swiftbackmeup_globals`
  * `swiftbackmeup_modes`
  * `swiftbackmeup_gits`
  * `swiftbackmeup_files`
  * `swiftbackmeup_postgresqls`
  * `swiftbackmeup_mariadbs`


## Dependencies

None.

## Example Playbook

    - hosts: db-servers
      become: yes
      vars_files:
        - vars/main.yml
      roles:
        - { role: Spredzy.swiftbackmeup }

*Inside `vars/main.yml`*:


    swiftbackmeup_crons:
      daily:
        minute: 0
        hour: 2
        job: 'swiftbackmeup --mode daily'
      weekly:
        day: '*/7'
        minute: 0
        hour: 3
        job: 'swiftbackmeup --mode weekly'

    swiftbackmeup_globals:
      create_container:
        value: True
      swift_container:
        value: True
      os_username:
        value: os_user
      os_password:
        value: os_password
      os_tenant_name:
        value: os_tenant_name
      os_region_name:
        value: os_region_name
      os_auth_url:
        value: os_auth_url

    swiftbackmeup_modes:
      daily:
        retention: 7
        pattern: "%Y%m%d"

    swiftbackmeup_gits:
      mygit_project:
        path: /srv/git/my_gitproject
        swift_container: git_backups
        subscriptions:
          - daily
          - now

    swiftbackmeup_files:
      my_special_file:
        path: /srv/www/picture/afile
        swift_container: file_backups
        swift_pseudo_folder: personal
        subscriptions:
          - daily
          - now

    swiftbackmeup_postgresqls:
      mypgdb1:
        database: mypgdb1
        subscriptions:
          - daily
          - now

    swiftbackmeup_mariadbs:
      mydb1:
        database: mydb1
        subscriptions:
          - daily
          - now


## License

Apache 2.0

## Author Information

Yanis Guenane <yguenane@redhat.com>
