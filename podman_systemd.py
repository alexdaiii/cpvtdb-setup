import asyncio
from dataclasses import dataclass
import getpass
import glob
import os
import sys
from typing import Literal

import argparse

__version__ = "1.2.0"

script = "%h/.local/bin/podman-compose"

@dataclass
class Args:
    action: Literal["register", "list", "ls", "create-unit"]


@dataclass
class Compose:
    project_name: str
    environ: dict

    def __init__(self):

        # project name is the name of the directory where the compose file is located
        self.project_name = os.path.basename(os.getcwd())

        # must be docker-compose.yml or docker-compose.yaml
        compose_file = None
        for fn in ("docker-compose.yml", "docker-compose.yaml"):
            if os.path.exists(fn):
                compose_file = fn
                break

        if not compose_file:
            raise ValueError(
                "No docker-compose.yml or docker-compose.yaml file found")

        self.environ = {
            # default values
            "COMPOSE_PROJECT_DIR": os.getcwd(),
            # get the absolute path to the file
            "COMPOSE_FILE": os.path.abspath(compose_file),
        }

        # Load .env from the Compose file's directory
        env_file = os.path.join(os.getcwd(), ".env")

        if os.path.exists(env_file):
            print(f"Loading environment variables from {env_file}")
            with open(env_file) as f:
                for line in f:
                    if line.startswith("#"):
                        continue
                    k, v = line.strip().split("=", 1)

                    # check if k, v are not empty
                    if k and v:
                        self.environ[k] = v
                    else:
                        print(f"Invalid line in {env_file}: {line}")


async def compose_systemd(
        *,
        args: Args,
):
    """
    create systemd unit file and register its compose stacks

    Copied from https://github.com/containers/podman-compose/blob/main/podman_compose.py#L2249C1-L2249C42
    """
    stacks_dir = ".config/containers/compose/projects"

    # register the compose file. Must be the same dir as a compose file you want to make into
    # a systemd unit file
    if args.action == "register":

        compose = Compose()

        proj_name = compose.project_name
        fn = os.path.expanduser(f"~/{stacks_dir}/{proj_name}.env")
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        # log.debug("writing [%s]: ...", fn)
        with open(fn, "w", encoding="utf-8") as f:
            for k, v in compose.environ.items():
                f.write(f"{k}={v}\n")
        # log.debug("writing [%s]: done.", fn)
        # log.info("\n\ncreating the pod without starting it: ...\n\n")
        username = getpass.getuser()
        print(
            f"""
you can use systemd commands like enable, start, stop, status, cat
all without `sudo` like this:

\t\tsystemctl --user enable --now 'podman-compose@{proj_name}'
\t\tsystemctl --user status 'podman-compose@{proj_name}'
\t\tjournalctl --user -xeu 'podman-compose@{proj_name}'

and for that to work outside a session
you might need to run the following command *once*

\t\tsudo loginctl enable-linger '{username}'

you can use podman commands like:

\t\tpodman pod ps
\t\tpodman pod stats 'pod_{proj_name}'
\t\tpodman pod logs --tail=10 -f 'pod_{proj_name}'
"""
        )
    elif args.action in ("list", "ls"):
        ls = glob.glob(os.path.expanduser(f"~/{stacks_dir}/*.env"))
        for i in ls:
            print(os.path.basename(i[:-4]))
    elif args.action == "create-unit":

        fn = "/etc/systemd/user/podman-compose@.service"

        print(
            "Creating the default base systemd unit file at /etc/systemd/user/podman-compose@.service")
        print(
            "NOTE: This requires sudo or root access to write to /etc/systemd/user/podman-compose@.service")

        out = f"""\
# {fn}

[Unit]
Description=%i rootless pod manual (podman-compose)

[Service]
Type=simple
EnvironmentFile=%h/{stacks_dir}/%i.env
ExecStartPre=-{script} up --no-start
ExecStartPre={script} up -d
ExecStart={script} wait
ExecStop={script} stop


[Install]
WantedBy=default.target
"""

        if os.access(os.path.dirname(fn), os.W_OK):
            # log.debug("writing [%s]: ...", fn)
            with open(fn, "w", encoding="utf-8") as f:
                f.write(out)
            # log.debug("writing [%s]: done.", fn)
            print(
                """
while in your project type `podman-compose systemd -a register. NOTE: if your .env file changes, you need to re-register the project`
"""
            )
        else:
            print(out)
            print("ERROR: Could not write to [%s], use 'sudo'")
            sys.exit(1)
            # log.warning("Could not write to [%s], use 'sudo'", fn)\


def arg_parser():
    """
    Parse the command line args.

    This file should be used like: python3 podman_systemd.py <action>
    """
    parser = argparse.ArgumentParser(
        description="podman-compose systemd unit file creator")
    parser.add_argument("action",
                        choices=["register", "list", "ls", "create-unit"])
    return parser.parse_args()


async def main():
    """
    Main entry point for the script.
    """

    args = arg_parser()

    if args.action not in ["register", "list", "ls", "create-unit"]:
        print(
            "Invalid action. Must be one of 'register', 'list', 'ls', 'create-unit'")
        sys.exit(1)

    args = Args(action=args.action)

    try:
        await compose_systemd(args=args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
