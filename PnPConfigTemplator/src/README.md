
## Config Directory
Contains two files.  
- apic_config.py has the name and login credentials for APIC-EM
- pnp_config.py has the directory for the templates and configuration files as they are generated.  The default is the work_files directory

## work_files
Contains the inventory files
Also contains directories for templates and configuration files

The templates are built from a base.jnja file.  There are specific templates for 1-2-3-4 switch stacks.  The interfaces are generated dynamically.

When rules are created, it is based on the number of switches in the stack.
The hosts.csv file contains the following variables
HOSTNAME,serialNumber,platformId,site,USERVLAN,VoiceVlan,management,DISTRO,ManagementIP,stackCount,template,imageFile

In theory "template" could be derived from "stackCount" and "platformId"

## 00test_jinja.py


## 10_create_and_upload.py
This requires an argument of an inventory file to use.
Creates configuration files based on template (work_files/templates) in work_files/configs
The template name is specified in the inventory file

This configuration file is then uploaded into the configuration repository on the controller.

It the creates the project (if required)

and creates a rule in the project for the specific device.  The rule contains all information required for PnP

## 12_clean_up_all.py
This requires an argument of an inventory file to use.  All projects in this inventory file will be removed.
NOTE: You should not have same project in two different inventory files

## list_all_projects
list all projects and rules
