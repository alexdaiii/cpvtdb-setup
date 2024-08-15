# CPVT Database Setup

Setups the CPVT database web app on a remote Debian/Ubuntu server.

## How to run

```{shell}
ansible-playbook -i hosts.yaml -e @secrets_file.yaml --ask-vault-pass --ask-become-pass ./playbooks/playbook.yaml
```
