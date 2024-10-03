# linux_vm_creation_app

Program designed to create a Linux server cloned from a template in vCenter.

## Description

This project provides a Python-based graphical user interface (GUI) to automate the creation of Linux virtual machines (VMs) in a VMware vCenter environment. The app allows users to select templates, configure deployment settings, and clone VMs into designated folders in vCenter.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/AbeFN/linux_vm_creation_app.git
    ```
2. **Install dependencies**:
   Make sure you have Python installed. Then, install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
3. **VMware Python SDK**:
   Install the PyVim and PyVmomi libraries to interact with vCenter:
    ```bash
    pip install pyvim pyvmomi
    ```

## Usage

1. Run the Python script:
    ```bash
    python server_creation_gui.py
    ```
2. Follow the on-screen prompts to:
   - Log into vCenter
   - Select a datacenter, folder, and template
   - Deploy a Linux VM based on your chosen settings.

## Features

- **GUI-Based Deployment**: A user-friendly interface for selecting templates and configuring deployment settings.
- **Automated Cloning**: Efficiently clones Linux VMs from predefined templates in vCenter.
- **Datacenter and Folder Selection**: Dynamically choose the datacenter and folder for the new VM.
- **Template Management**: Automatically fetches and lists available templates for deployment.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m "Add new feature"`).
4. Push your branch (`git push origin feature-branch`).
5. Submit a pull request for review.

