#!/usr/bin/env python

import csv
import json
import os
import os.path
from argparse import ArgumentParser
import jinja2
from login import login

from config.pnp_config import DEVICES, TEMPLATE_DIR, CONFIGS_DIR


def lookup_and_create(apic, project_name):
    project_name = project_name
    project = apic.pnpproject.getPnpSiteByRange(siteName=project_name)

    if project.response != []:
        project_id = project.response[0].id
    else:
        # create it
        print ("creating project:{project}".format(project=project_name))
        pnp_task_response= apic.pnpproject.createPnpSite(project=[{'siteName' :project_name}])
        task_response = apic.task_util.wait_for_task_complete(pnp_task_response, timeout=5)

        # 'progress': '{"message":"Success creating new site","siteId":"6e059831-b399-4667-b96d-8b184b6bc8ae"}'
        progress = task_response.progress
        project_id = json.loads(progress)['siteId']

    return project_id

# this is due to lack of parameterized search aPI
def is_file_present(apic, namespace, filename):
    filename = filename
    file_list = apic.file.getFilesByNamespace(nameSpace=namespace)
    fileid_list = [file.id for file in file_list.response if file.name == filename]
    return None if fileid_list == [] else fileid_list[0]


def upload_file(apic, filename):
    file_id = is_file_present(apic, "config", os.path.basename(filename))
    if file_id is not None:
        print ("File %s already uploaded: %s" %(filename, file_id))
        return file_id

    file_result = apic.file.uploadFile(nameSpace="config", fileUpload=filename)
    file_id = file_result.response.id
    print("Configuration File_id:", file_id)
    return file_id

def create_rule(apic, param_dict, project_id, file_id):
    serial_number = param_dict['serialNumber']
    rule_data = [{
        "serialNumber": serial_number,
        "platformId":  param_dict['platformId'],
        "hostName": param_dict['HOSTNAME'],
        "configId" : file_id,
        "pkiEnabled": True
}]
    if param_dict['imageFile']:
        image_id = is_file_present(apic, "image", param_dict['imageFile'])
        if not image_id:
            raise ValueError("No image %s on controller", param_dict['imageFile'])
        rule_data[0]['imageId'] = image_id
    if int(param_dict['stackCount']) > 1:
        rule_data[0]['memberCount'] = param_dict['stackCount']
        rule_data[0]["licenseLevel"] =  "ipbase"
        rule_data[0]["eulaAccepted"] = True

    print("Creating Rule", json.dumps(rule_data,indent=2))
    rule_task = apic.pnpproject.createPnpSiteDevice(projectId=project_id, rule=rule_data)
    task_response = apic.task_util.wait_for_task_complete(rule_task, timeout=5)
    progress = task_response.progress
    print("Rule Status:", progress)

def create_and_upload(apic, devices, template_dir):

    f = open(devices, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            print ("Variables:",device_row)
            templateLoader = jinja2.FileSystemLoader( searchpath=[".", template_dir])
            templateEnv = jinja2.Environment( loader=templateLoader )
            template = templateEnv.get_template(device_row['template'])
            outputText = template.render(device_row)
            config_filename = CONFIGS_DIR + device_row['HOSTNAME'] + '-config'
            with open(config_filename, 'w') as config_file:
                config_file.write(outputText)
            print("created file: %s" % config_filename)

            project_id = lookup_and_create(apic, device_row['site'])
            file_id = upload_file(apic, config_filename)
            create_rule (apic, device_row, project_id, file_id)
            print()

    finally:
        f.close()

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument( 'devices', type=str,
            help='device inventory csv file')
    args = parser.parse_args()

    apic = login()
    print ("Using device file:", args.devices)
    print ("Using template directory:", TEMPLATE_DIR)
    print ("##########################")
    create_and_upload(apic, devices=args.devices, template_dir=TEMPLATE_DIR)
