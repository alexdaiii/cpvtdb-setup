# CPVT Database Setup

Setups the CPVT database web app on a remote Debian/Ubuntu server.

## Requirements

Run the following command to install the requirements

```{shell}
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

It will install:

- ansible
- passlib

## Creating a Secrets File

Here are some of the variables that you will need in the secrets file:

- zenodo_token
  - The token to access the Zenodo API. To get this token, you need to create an account on Zenodo and create a new API token.
  Instructions can be found [on Zenodo](https://developers.zenodo.org/#quickstart-upload).
- deposition_id
  - The id of the Zenodo deposition which will be downloaded and used to populate the database.
  - The deposition id for the CPVT database is [13256077](https://zenodo.org/records/13256077)
- CF_TUNNEL_TOKEN
  - This will be passed as an environment variable to the cloudflare/cloudflared docker container.
  - To obtain this token, you need to create a tunnel on [Cloudflare](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/)
  - This will make your server accessible outside of your network, without port forwarding. However, if you do not want to use this feature, 
  you can remove the cloudflared container from the `docker-compose.yaml` file.

## How to run

1. Create a secrets file. An example file is provided in `secrets_file_example.yaml`. You can copy it and modify it to your needs.
2. Create a `hosts.yaml` file with the IP address of the server you want to deploy the app to. An example file is provided in `hosts_example.yaml`.
    - You must have a user with sudo privileges on the server.
    - You must have an SSH key pair to access the server.
3. Run the following command:
    ```{shell}
    ansible-playbook -i hosts.yaml -e @secrets_file.yaml --ask-vault-pass --ask-become-pass ./playbooks/playbook.yaml
    ```
    - Note: This assumes that the secrets file is encrypted. If it is not, you can remove the `--ask-vault-pass` flag.
