# Terraform and Ansible Demon on cloudscale.ch

This demo show how to use the cloudscale.ch Terraform provider and the
cloudscale.ch Ansible module to create a simple pair of highly
available webservers using keepalived and nginx.

## Prerequisites

* Git
* Python 3

## Run the demo

### Checkout the demo code

    git clone https://github.com/cloudscale-ch/terraform-ansible-demo.git
    cd terraform-ansible-demo

### Get and set API token

Go to https://control.cloudscale.ch/user/api-tokens and create a read/write API token

    # Set API token environment variable for Rerraform
    export CLOUDSCALE_TOKEN=xxxx
    
    # Set API token environment variable for Ansible
    export CLOUDSCALE_API_TOKEN=$CLOUDSCALE_TOKEN

### Install Terraform

Download the terraform binary for your platform form https://www.terraform.io/downloads.html and unzip it

### Install Ansible

    python3 -m venv ansible-venv
    . ansible-venv/bin/activate
    pip install ansible

### Create the VMs using Terraform

    # Configure your SSH key in terraform.tfvars
    vi terraform.tfvars
    
    # Initialize terraform
    ./terraform init
    
    # Create VMs
    ./terraform apply

### See the cloudscale.ch inventory plugin in action

    ansible-inventory -i inventory.yml --graph

### Configure VMs using Ansible

    ansible-playbook -i inventory.yml ha-webservers.yml

### Check the webserver works

    # Use curl to access the cloudscale.ch API to get the floating IP
    # created by Ansible
    # Set the authorization header
    AUTH_HEADER="Authorization: Bearer $CLOUDSCALE_API_TOKEN"
    
    # Call the API with curl
    curl -H "$AUTH_HEADER" https://api.cloudscale.ch/v1/floating-ips

You can now access your HA webserver at http://<floating_ip>/.

    # Connect to your server keepalived01
    ssh debian@<your-server-ip>

    # Turn the server off
    poweroff

If you now access your HA webserver again using the same floating IP
you will see that it switched over to server keepalived00.
    
### Teardown everything again

    ./terraform destroy
