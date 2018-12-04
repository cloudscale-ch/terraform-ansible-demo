# Terraform and Ansible demo on cloudscale.ch IaaS platform

This demo will show you how to use the [cloudscale.ch Terraform Provider](https://www.terraform.io/docs/providers/cloudscale/index.html) and the [cloudscale.ch Ansible Cloud Module](https://docs.ansible.com/ansible/latest/modules/cloudscale_server_module.html) to create a pair of highly available web servers using keepalived and nginx.

## Prerequisites

* Git
* Python 3

## Run the demo

### Checkout the demo code

    git clone https://github.com/cloudscale-ch/terraform-ansible-demo.git
    cd terraform-ansible-demo

### Get and set the API token

Go to https://control.cloudscale.ch/user/api-tokens and create a read/write API token

    # Set API token environment variable for Terraform
    export CLOUDSCALE_TOKEN=xxxx
    
    # Set API token environment variable for Ansible
    export CLOUDSCALE_API_TOKEN=$CLOUDSCALE_TOKEN

### Install Terraform

Download the Terraform binary for your platform at https://www.terraform.io/downloads.html and unzip it

### Install Ansible

    python3 -m venv ansible-venv
    . ansible-venv/bin/activate
    pip install ansible

### Create your cloud servers using Terraform

    # Configure your SSH key in terraform.tfvars
    vi terraform.tfvars
    
    # Initialize terraform
    ./terraform init
    
    # Launch your cloud servers
    ./terraform apply

### See the cloudscale.ch inventory plugin in action

    ansible-inventory -i inventory.yml --graph

### Configure your cloud servers using Ansible

    ansible-playbook -i inventory.yml ha-webservers.yml

### Verify that the web server(s) works

    # Use curl to access the cloudscale.ch API to get the Floating IP
    # created by Ansible
    
    # Set the authorization header first
    AUTH_HEADER="Authorization: Bearer $CLOUDSCALE_API_TOKEN"
    
    # Call the API with curl
    curl -H "$AUTH_HEADER" https://api.cloudscale.ch/v1/floating-ips

You can now access your highly available web server at http://<floating_ip>/. Once you shut down the currently active web server you will notice that the Floating IP will automatically switch over to the other web server:

    # Show your Terraform infrastructure to display the IP addresses of your cloud servers
    ./terraform show
    
    # Connect to the currently active web server
    ssh debian@<your-server-ip>
    
    # Turn the server off
    sudo poweroff

If you now access your highly available web server again using the same Floating IP
you will see that it switched over to the server keepalived00.
    
### Tear down everything

    ./terraform destroy
