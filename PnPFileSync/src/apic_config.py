import os
APIC= os.getenv("APIC") or "adam-iwan"
APIC_USER= os.getenv("APIC_USER") or "admin"
APIC_PASSWORD= os.getenv("APIC_PASSWORD") or "password"
DIR=os.getenv('PNP_DIR') or "../files"