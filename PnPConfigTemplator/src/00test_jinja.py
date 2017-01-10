#!/usr/bin/env python

import csv
from argparse import ArgumentParser
import jinja2
from login import login
from config.pnp_config import DEVICES, TEMPLATE_DIR, CONFIGS_DIR


def create_and_upload(apic, devices, template_dir):


    f = open(devices, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            print (device_row)
            templateLoader = jinja2.FileSystemLoader( searchpath=[".", template_dir])
            templateEnv = jinja2.Environment( loader=templateLoader )
            template = templateEnv.get_template(device_row['template'])
            outputText = template.render(device_row)
            config_filename = CONFIGS_DIR + device_row['HOSTNAME'] + '-config'
            with open(config_filename, 'w') as config_file:
                config_file.write(outputText)
            print("created file: %s" % config_filename)


    finally:
        f.close()

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument( 'devices', type=str,
            help='device inventory csv file')
    args = parser.parse_args()
    apic = None
    create_and_upload(apic, devices=args.devices, template_dir=TEMPLATE_DIR)