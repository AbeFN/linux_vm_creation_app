#server_creation_gui

from tkinter import Tk, Label, Entry, Button, OptionMenu, StringVar, messagebox
from vcenter_logic import connect_to_vcenter, fetch_vcenter_data, create_server
from pyVmomi import vim

# Initialize Global Variables
content = None

# Step 1: Login Screen
def show_login_screen():
    login_root = Tk()
    login_root.title("vCenter Login")
    login_root.geometry("550x200")

    vcenter_ip_var = StringVar()
    username_var = StringVar()
    password_var = StringVar()

    Label(login_root, text="vCenter Hostname/IP").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    Entry(login_root, textvariable=vcenter_ip_var, width=30).grid(row=0, column=1, padx=5, pady=5)

    Label(login_root, text="Username").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    Entry(login_root, textvariable=username_var, width=30).grid(row=1, column=1, padx=5, pady=5)

    Label(login_root, text="Password").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    Entry(login_root, textvariable=password_var, width=30, show='*').grid(row=2, column=1, padx=5, pady=5)

    def authenticate():
        vcenter_ip = vcenter_ip_var.get()
        username = username_var.get()
        password = password_var.get()

        global content
        si = connect_to_vcenter(vcenter_ip, username, password)
        print(si)  # Check if si is valid
        if si:
            content = si.RetrieveContent()  # Retrieve the actual content here
            login_root.destroy()
            show_template_selection_screen()  # Proceed to the next screen
        else:
            messagebox.showerror("Login Failed", "Incorrect username and/or password. Please try again.")


    Button(login_root, text="Sign in", command=authenticate).grid(row=3, column=1, pady=10)
    Button(login_root, text="Close", command=login_root.destroy).grid(row=3, column=0, pady=10)

    login_root.mainloop()

# Fetch templates within a folder
def fetch_templates_in_folder(folder):
    templates = []
    for entity in folder.childEntity:
        if isinstance(entity, vim.Folder):
            templates.extend(fetch_templates_in_folder(entity))
        elif isinstance(entity, vim.VirtualMachine) and entity.config.template:
            templates.append(entity.name)
    return templates

# Step 2: Template Selection Screen
def show_template_selection_screen():
    selection_root = Tk()
    selection_root.title("Template Selection")
    selection_root.geometry("400x400")

    datacenter_name_var = StringVar()
    cluster_name_var = StringVar()
    datastore_name_var = StringVar()
    folder_name_var = StringVar()
    template_name_var = StringVar()

    # Disable "Next" button initially
    next_button = Button(selection_root, text="Next", state="disabled", 
                     command=lambda: show_vm_naming_screen(template_name_var.get(), 
                                                           folder_name_var.get(), 
                                                           cluster_name_var.get(), 
                                                           datastore_name_var.get(), 
                                                           datacenter_name_var.get(),
                                                           folders))  # Pass the list of folders

    next_button.grid(row=10, column=1, pady=10)

    def populate_fields():
        global folders
        templates, datacenters, clusters, datastores, folders = fetch_vcenter_data(content)  # Pass 'content'

        print(f"Datacenters: {datacenters}")
        print(f"Clusters: {clusters}")
        print(f"Datastores: {datastores}")
        print(f"Folders: {folders}")

        # Populate datacenter OptionMenu
        if datacenters:
            datacenter_name_var.set(datacenters[0])
            datacenter_menu['menu'].delete(0, 'end')
            for datacenter in datacenters:
                datacenter_menu['menu'].add_command(label=datacenter, command=lambda dc=datacenter: datacenter_name_var.set(dc))

        # Populate cluster OptionMenu
        if clusters:
            cluster_name_var.set(clusters[0])
            cluster_menu['menu'].delete(0, 'end')
            for cluster in clusters:
                cluster_menu['menu'].add_command(label=cluster, command=lambda cl=cluster: cluster_name_var.set(cl))

        # Populate datastore OptionMenu
        if datastores:
            datastore_name_var.set(datastores[0])
            datastore_menu['menu'].delete(0, 'end')
            for datastore in datastores:
                datastore_menu['menu'].add_command(label=datastore, command=lambda ds=datastore: datastore_name_var.set(ds))

        # Populate folder OptionMenu
        if folders:
            folder_name_var.set(folders[0])
            folder_menu['menu'].delete(0, 'end')
            for folder in folders:
                folder_menu['menu'].add_command(label=folder, command=lambda f=folder: folder_name_var.set(f))

    def fetch_templates():
        selected_folder = folder_name_var.get()  # Get the selected folder from the dropdown

    # Now use selected_folder instead of the undefined variable
        for dc in content.rootFolder.childEntity:
            for folder in dc.vmFolder.childEntity:
                if isinstance(folder, vim.Folder) and folder.name == selected_folder:
                    templates = fetch_templates_in_folder(folder)
                    if templates:
                        template_name_var.set(templates[0])
                        template_menu['menu'].delete(0, 'end')
                        for template in templates:
                            template_menu['menu'].add_command(label=template, command=lambda temp=template: template_name_var.set(temp))
                        next_button.config(state="normal")  # Enable "Next" button once a template is selected
                    else:
                        messagebox.showwarning("No Templates", "No templates found in this folder.")

    # Create widgets for datacenter, cluster, datastore, and folder
    Label(selection_root, text="Datacenter").grid(row=0, column=0, padx=5, pady=5)
    datacenter_menu = OptionMenu(selection_root, datacenter_name_var, [])
    datacenter_menu.grid(row=0, column=1, padx=5, pady=5)

    Label(selection_root, text="Cluster").grid(row=1, column=0, padx=5, pady=5)
    cluster_menu = OptionMenu(selection_root, cluster_name_var, [])
    cluster_menu.grid(row=1, column=1, padx=5, pady=5)

    Label(selection_root, text="Datastore").grid(row=2, column=0, padx=5, pady=5)
    datastore_menu = OptionMenu(selection_root, datastore_name_var, [])
    datastore_menu.grid(row=2, column=1, padx=5, pady=5)

    Label(selection_root, text="Folder").grid(row=3, column=0, padx=5, pady=5)
    folder_menu = OptionMenu(selection_root, folder_name_var, [])
    folder_menu.grid(row=3, column=1, padx=5, pady=5)

    # Button to fetch templates
    Button(selection_root, text="Fetch Templates", command=fetch_templates).grid(row=4, column=1, padx=5, pady=5)

    # Template selection OptionMenu
    Label(selection_root, text="Template").grid(row=5, column=0, padx=5, pady=5)
    template_menu = OptionMenu(selection_root, template_name_var, [])
    template_menu.grid(row=5, column=1, padx=5, pady=5)

    # Back button
    Button(selection_root, text="Back", command=lambda: selection_root.destroy()).grid(row=10, column=0, pady=10)

    populate_fields()  # Populate the datacenter, cluster, datastore, and folder fields

    selection_root.mainloop()


# Step 3: VM Naming Screen
def show_vm_naming_screen(template_name, folder_name, cluster_name, datastore_name, datacenter_name, folder_list):
    naming_root = Tk()
    naming_root.title("VM Naming")
    naming_root.geometry("350x200")

    folder_selection_var = StringVar()  # Variable to hold selected folder
    folder_selection_var.set(folder_name)  # Set the default folder

    vm_name_entry = Entry(naming_root)  # Create an Entry widget for VM name input
    vm_name_entry.grid(row=0, column=1, padx=5, pady=5)  # Position the entry field

    Label(naming_root, text="VM Name").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    Label(naming_root, text="Folder").grid(row=1, column=0, padx=5, pady=5, sticky='e')

    # OptionMenu for folder selection
    folder_menu = OptionMenu(naming_root, folder_selection_var, *folder_list)
    folder_menu.grid(row=1, column=1, padx=5, pady=5)

    def create_vm():
        vm_name = vm_name_entry.get().strip()  # Directly get the text from the Entry widget
        selected_folder = folder_selection_var.get()  # Get selected folder from OptionMenu

        print(f"Creating VM: {vm_name} in folder: {selected_folder}")  # Debug print

        if not vm_name:
            messagebox.showerror("Error", "VM name cannot be empty.")
            return

        if not selected_folder:
            messagebox.showerror("Error", "Please select a folder.")
            return

        try:
            create_server(content, vm_name, datacenter_name, cluster_name, datastore_name, template_name, selected_folder)
            naming_root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # Final "Create" button to build the VM
    Button(naming_root, text="Create VM", command=create_vm).grid(row=3, column=1, pady=10)

    naming_root.mainloop()




# Run the login screen to start the application
show_login_screen()
