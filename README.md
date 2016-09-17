Role
====

This role is an addon for others roles created by us, all roles example for site.yml:

``` yaml
- name: apply Nagios settings
  hosts: nagios4_servers
  become: yes
  become_method: sudo
  roles:
    - { role: nagios4_server, tags: ["install", "nagios4_server_all", "nagios4_server"] }
    - { role: nagios4_server_plugins, tags: ["install", "nagios4_server_all", "nagios4_server_plugins"] }
    - { role: nagios4_server_pnp4nagios, tags: ["install", "nagios4_server_all", "nagios4_server_pnp4nagios"] }
    - { role: nagios4_server_snmptrap, tags: ["install", "nagios4_server_all", "nagios4_server_snmptrap"] }
    - { role: ANXS.mysql, tags: ["install", "nagios4_server_all", "nagios4_server_thruk", "ANXS.mysql"] }
    - { role: nagios4_server_thruk, tags: ["install", "nagios4_server_all", "nagios4_server_thruk"] }
    - { role: postfix_client, tags: ["install", "nagios4_server_all", "postfix_client"] }
# Additional tags: in roles/tag
# nagios4_server             - config_nagios
# nagios4_server             - nagios4_server_main_config
# nagios4_server             - config_nagios_cron
# nagios4_server_plugins     - config_nagios_plugins
# nagios4_server_plugins     - test_nagios_plugins
# nagios4_server_pnp4nagios  - test_nagios_pnp4nagios
# nagios4_server_thruk       - config_nagios_thruk_cron
# nagios4_server_thruk       - test_nagios_thruk
# nagios4_server_thruk_git   - config_nagios_thruk_git_cron
# nagios4_server_snmptrap    - config_nagios
```

We don't use meta dependencies due to the lack of option to not run the dependency when I want to run only one of these tasks in a role.

Download MIBs
=============

How I downloaded mibs to files/mibs?

    wget -c ftp://ftp.cisco.com/pub/mibs/v2/*-MIB.my 

I didn't add all mibs. 
I have also cloned netdisco mibs to `/var/lib/mibs/netdisco-mibs`
And uncommented cisco and rfc lines in `/etc/snmp/snmp.conf`
example: 

    mibdirs +/var/lib/mibs/netdisco-mibs/rfc

Translate MIBs
==============

NOTE: SNMP_TRAP is de service name that it will submit the check result

Example 1: 

snmpttconvertmib --in=/usr/share/snmp/mibs/SNMPv2-MIB.my --out=/etc/snmp/snmptt.conf.prime --exec='/usr/local/nagios/libexec/submit_check_result $r SNMP_TRAP 1'
snmpttconvertmib --in=/usr/share/snmp/mibs/CISCO-CONFIG-MAN-MIB.my --out=/etc/snmp/snmptt.conf.cisco.config --exec='/usr/local/nagios/libexec/submit_check_result $r SNMP_TRAP 1'

Example 2:

snmpttconvertmib --in=/usr/share/snmp/mibs/CISCO-IF-EXTENSION-MIB.my --out=/etc/snmp/snmptt.conf.cisco.if --exec='/usr/local/nagios/libexec/submit_check_result $r SNMP_TRAP 1'
snmpttconvertmib --in=/usr/share/snmp/mibs/IF-MIB.my --out=/etc/snmp/snmptt.conf.if --exec='/usr/local/nagios/libexec/submit_check_result $r SNMP_TRAP 1'

    # $r is hostname (because we have dns activated, and system should resolve the ip to host)
    # SNMP_TRAP is service name in nagios (service asociated with host
    # 1 is return_code (An integer that determines the state
    #       of the service check, 0=OK, 1=WARNING, 2=CRITICAL,
    #       3=UNKNOWN).
    # $0 is oid translated
    # $* all descriptions translated
    # See http://snmptt.sourceforge.net/docs/snmptt.shtml#SNMPTT.CONF-FORMAT for vars

I have modified snmptt.conf.cisco.if, ifstatusUp to OK (0) and ifStatusDown to Critical (2)
Same done with snmptt.conf.cisco.config so config traps will be OK.

You can use these examples to help extending th required translations for your needs and then make a pull request to incorporate them on this role.

Cisco Configuration
===================

http://www.cisco.com/c/en/us/td/docs/ios/12_2/configfun/command/reference/ffun_r/frf014.html#wp1116543

When an SNMP trap or inform is sent from a Cisco SNMP server, it has a notification address of whatever interface it happened to go out of at that time. Use this command monitor notifications from a particular interface.  

    snmp-server trap-source id

Example: Cisco 3560

    snmp-server trap-source Vlan85
    snmp-server enable traps snmp linkdown coldstart warmstart
    snmp-server enable traps cpu threshold
    snmp-server enable traps vtp
    snmp-server enable traps vlancreate
    snmp-server enable traps vlandelete
    snmp-server enable traps flash insertion removal
    snmp-server enable traps port-security trap-rate 10
    snmp-server enable traps envmon fan shutdown supply temperature status
    snmp-server enable traps storm-control trap-rate 100
    snmp-server enable traps copy-config
    snmp-server enable traps stpx root-inconsistency loop-inconsistency
    snmp-server enable traps syslog 
    snmp-server host ip.address version 2c public
    no snmp-server enable traps snmp linkup
    
Example: Cisco 6500

    snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart
    snmp-server trap-source Vlan85
    snmp-server enable traps cpu threshold
    snmp-server enable traps tty
    snmp-server enable traps vtp
    snmp-server enable traps vlancreate
    snmp-server enable traps vlandelete
    snmp-server enable traps copy-config
    snmp-server enable traps fru-ctrl
    snmp-server enable traps flash insertion removal
    snmp-server enable traps syslog
    snmp-server enable traps stpx inconsistency root-inconsistency loop-inconsistency 
    snmp-server enable traps envmon fan shutdown supply temperature status
    snmp-server enable traps hsrp
    snmp-server enable traps vlan-membership


Example: Cisco 6509 Core Router With VRF’s defined
    
    snmp-server community public RO
    snmp-server trap-source Vlan5
    snmp-server enable traps chassis
    snmp-server enable traps module
    snmp-server enable traps transceiver all
    snmp-server enable traps bgp
    snmp-server enable traps config-copy  <- REMOVE AFTER TESTING
    snmp-server enable traps config       <- REMOVE AFTER TESTING
    snmp-server enable traps stpx inconsistency root-inconsistency loop-inconsistency
    snmp-server enable traps envmon fan shutdown supply temperature status
    snmp-server enable traps errdisable
    snmp-server host 192.168.5.5 vrf INTERNAL public

Example: Cisco Nexus 5596 Aggregation Layer
    
    snmp-server contact Paul Porter
    snmp-server source-interface trap Vlan5
    snmp-server source-interface inform Vlan5
    snmp-server user admin network-admin auth localizedkey
    snmp-server host 192.168.5.5 traps version 2c public
    snmp-server host 192.168.5.5 use-vrf default
    snmp-server enable traps bridge newroot
    snmp-server enable traps bridge topologychange
    snmp-server enable traps stpx inconsistency
    snmp-server enable traps stpx root-inconsistency
    snmp-server enable traps stpx loop-inconsistency
    snmp-server community public group network-operator

Example: Cisco 2960S Access Layer

    snmp-server community public RO
    snmp-server enable traps bridge topologychange
    snmp-server enable traps envmon fan shutdown supply temperature status
    snmp-server enable traps errdisable
    snmp-server host 192.168.5.5 version 2c public

Example: Cisco ASA 5520 Remote Access VPN

    snmp-server host inside 192.168.5.5 community public
    snmp-server community public
    snmp-server enable traps entity config-change fru-insert fru-remove

Traps in interfaces:

    int gigabitEthernet 0/1
    snmp trap link-status

Verification
============

If you use for testing: 

    snmp-server enable traps config       <- REMOVE AFTER TESTING
    
You can test with

    write  # on cisco

*Verify also snmptranslate*

    snmptranslate -On CISCO-RHINO-MIB::ciscoLS1010ChassisFanLed
    .1.3.6.1.4.1.9.5.11.1.1.12  # should resolve this.

HP Configuration and MIBs
=========================

ftp://ftp.hp.com/pub/softlib2/software1/pubsw-windows/p307788654/v46168/upd800mib.zip 

Nagios Configuration: 
=====================

To enable this service in your nagios, add snmptrap_services.cfg, example: 

define service {
    use                 SNMP_TRAP
    hostgroup_name      switches,servers,etc
    check_interval      120 ; Don't clear for 2 hours
}


Internal Nagios configuration
=============================

This role configures for nagios: 

SNMP_TRAP template

snmptt service for translating traps
supervisor to manage snmptrapd service
snmptrapd to send traps received for snmptt. 

On snmptt: 
----------

It uses custom script for unkown traps, so you don't need to translate all of them: 

    submit_check_result_unknowns

Also uses standard script to send traps to nagios: 

    submit_check_result
    
VARS:
=====

http://docs.ansible.com/ansible/intro_inventory.html#splitting-out-host-and-group-specific-data

Name resolution is required for snmptraps, so I have added 3 ways to resolve this issue:

There is special script created to update hosts file, it updates all addressess in /etc/hosts file from nagios config information.
If your hosts are not resolved in DNS then you need this to ensure the ip addresses of traps are resolved to hosts in you nagios.  

Setup you group_vars/nagios4_servers (if your site.yml has nagios4_server): 

    nagios_update_hosts_file: true

If you have hosts in DNS you can add a list of domains to resolve:

    snmptt_strip_domain:
      - example.net
      - seconddomain.net

You can also define a variable with fixed hosts to add to hosts file: 

    hosts_names: true
    # example:
    # hosts_names:
    #   - { name: "hostname", ip: "addres" }


See more:
https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/passivechecks.html 

References
==========

https://paulgporter.net/2013/09/16/nagios-snmp-traps/

https://paulgporter.net/2013/09/16/nagios-snmp-traps/
https://assets.nagios.com/downloads/nagiosxi/docs/Integrating_SNMP_Traps_With_Nagios_XI.pdf
http://drivemeca.blogspot.com.uy/2013/10/como-instalar-snmp-trap-en-nagios.html
http://snmptt.sourceforge.net/docs/snmptt.shtml#Sample1-SNMPTT.CONF-file
http://net-snmp.sourceforge.net/wiki/index.php/TUT:Using_and_loading_MIBS

MIBs:
http://tools.cisco.com/ITDIT/MIBS/servlet/index
ftp://ftp.cisco.com/pub/mibs/v2/
ftp://ftp.hp.com/pub/softlib2/software1/pubsw-windows/p307788654/v46168/
https://sourceforge.net/p/netdisco/mibs/ci/master/tree/hp/
http://www.mibdepot.com/index.shtml?id=8750
https://github.com/att/vizgems/tree/master/mibs
http://net-snmp.sourceforge.net/docs/mibs/

Behind proxy
============

(only if you are behind proxy)

Add to your group_vars file:

    proxy_env:
      http_proxy: "http://user:pass@hostname:port"

It will help install pip package required by hosts script
