# vcenter_logic.py

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
from tkinter import messagebox


# Variables for vCenter hostname and SSL context
vcentername = "blrvcp.bloomlab.com"
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Connect to vCenter
def connect_to_vcenter(vcenter_ip, username, password):
    try:
        si = SmartConnect(host=vcenter_ip, user=username, pwd=password, sslContext=context)
        return si
    except vim.fault.InvalidLogin:
        messagebox.showerror("Connection Error", "Incorrect username and/or password connecting to Host. Get rekt. Please try again.")
        return None
    except Exception as e:
        messagebox.showerror("Connection Error", f"Could not connect to vCenter: {str(e)}")
        return None

# Fetch templates within a folder
def fetch_templates_in_folder(folder):
    templates = []
    for entity in folder.childEntity:
        if isinstance(entity, vim.Folder):
            templates.extend(fetch_templates_in_folder(entity))
        elif isinstance(entity, vim.VirtualMachine) and entity.config.template:
            templates.append(entity.name)
    return templates

# Fetch templates, datacenters, clusters, datastores, and folders
# Fetch templates, datacenters, clusters, datastores, and folders
def fetch_vcenter_data(content):  # Directly pass 'content' instead of 'si'
    templates, datacenters, clusters, datastores, folders = [], [], [], [], []

    # Fetching datacenters
    for dc in content.rootFolder.childEntity:  # Access the rootFolder in the retrieved content
        if isinstance(dc, vim.Datacenter):
            datacenters.append(dc.name)
            # Fetching clusters
            for cluster in dc.hostFolder.childEntity:
                if isinstance(cluster, vim.ClusterComputeResource):
                    clusters.append(cluster.name)
            # Fetching datastores
            for datastore in dc.datastore:
                datastores.append(datastore.name)
            # Fetching folders and templates
            for folder in dc.vmFolder.childEntity:
                if isinstance(folder, vim.Folder):
                    folders.append(folder.name)
                    templates.extend(fetch_templates_in_folder(folder))

    return templates, datacenters, clusters, datastores, folders


def find_vm_in_folder(folder, vm_name):
    for entity in folder.childEntity:
        if isinstance(entity, vim.Folder):
            vm = find_vm_in_folder(entity, vm_name)
            if vm:
                return vm
        elif isinstance(entity, vim.VirtualMachine) and entity.name == vm_name:
            return entity
    return None


# Function to spin up the server
def create_server(content, vm_name, datacenter_name, cluster_name, datastore_name, template_name, folder_name):
    try:
        # Get the datacenter
        datacenter = [dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name]
        if not datacenter:
            raise ValueError(f"Datacenter '{datacenter_name}' not found.")
        datacenter = datacenter[0]

        # Get the template
        template = find_vm_in_folder(datacenter.vmFolder, template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found.")

        # Get the cluster (if applicable)
        cluster = None
        if cluster_name:
            cluster = [cl for cl in datacenter.hostFolder.childEntity if cl.name == cluster_name]
            if not cluster:
                raise ValueError(f"Cluster '{cluster_name}' not found.")
            cluster = cluster[0]

        # Get the datastore
        datastore = [ds for ds in datacenter.datastore if ds.name == datastore_name]
        if not datastore:
            raise ValueError(f"Datastore '{datastore_name}' not found.")
        datastore = datastore[0]

        # Get the folder
        folder = [f for f in datacenter.vmFolder.childEntity if isinstance(f, vim.Folder) and f.name == folder_name]
        if not folder:
            raise ValueError(f"Folder '{folder_name}' not found.")
        folder = folder[0]

        # Function to find the host system
        def find_host_system(entity):
            if isinstance(entity, vim.HostSystem):
                return entity
            elif hasattr(entity, 'childEntity'):  # Check if the entity has children
                for child in entity.childEntity:
                    host = find_host_system(child)
                    if host:
                        return host
            return None

        # Check if we have a cluster
        if not cluster:
            # No cluster - check if there's a host
            host = find_host_system(datacenter.hostFolder)
            if host:
                resource_pool = host.resourcePool
            else:
                # Handle standalone ESXi host case
                host = [h for h in datacenter.hostFolder.childEntity if isinstance(h, vim.ComputeResource)]
                if host and host[0].resourcePool:
                    resource_pool = host[0].resourcePool
                else:
                    raise ValueError("No host or resource pool found.")
        else:
            # If a cluster is found, use the cluster resource pool
            resource_pool = cluster.resourcePool

        # Create relocation spec
        relocate_spec = vim.vm.RelocateSpec()
        relocate_spec.pool = resource_pool
        relocate_spec.datastore = datastore

        # Create clone spec
        clone_spec = vim.vm.CloneSpec()
        clone_spec.location = relocate_spec
        clone_spec.powerOn = True

        # Clone the template
        task = template.Clone(folder=folder, name=vm_name, spec=clone_spec)
        return task
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")




