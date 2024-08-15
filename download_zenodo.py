import json
import urllib.request
import argparse
import os


def get_args():
    """
    This file should be run with the following command:
    python download_zenodo.py --deposition_id 123456 --zenodo_token abcdefgh --output_dir /path/to/output
    """
    parser = argparse.ArgumentParser(
        description='Download files from a Zenodo deposition')
    parser.add_argument('--deposition_id', type=int, required=True,
                        help='The Zenodo deposition ID')
    parser.add_argument('--zenodo_token', type=str, required=False,
                        help='The Zenodo access token')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='The output directory to save the files')

    return parser.parse_args()


def main():
    args = get_args()

    zenodo_token = args.zenodo_token
    deposition_id = args.deposition_id

    uri = f"https://zenodo.org/api/deposit/depositions/{deposition_id}/files"

    # create the output directory if it does not exist
    print(f"Creating output directory {args.output_dir} if it does not exist")
    os.makedirs(args.output_dir, exist_ok=True)

    if zenodo_token is not None:
        uri += f"?access_token={zenodo_token}"
    else:
        print(
            "No Zenodo access token provided. Some files may not be accessible")

    # the content type is application/json
    headers = {'Content-Type': 'application/json'}
    request = urllib.request.Request(uri, headers=headers)

    with urllib.request.urlopen(request) as response:
        data = response.read()
        files_json = json.loads(data)

        print("Downloading files:")
        for files in files_json:
            download_file(files, args.output_dir, zenodo_token)


def download_file(
        file_info: dict, output_dir: str, zenodo_token: str = None) -> None:
    download_link_base = file_info["links"]["download"]
    download_link = download_link_base

    filename = file_info["filename"]

    if zenodo_token is not None:
        download_link += f"?access_token={zenodo_token}"

    print(f"Downloading {filename} from {download_link_base}")

    output_path = os.path.join(output_dir, filename)

    with urllib.request.urlopen(download_link) as response:
        with open(output_path, 'wb') as out_file:
            out_file.write(response.read())

    print(f"Downloaded {filename} to {output_path}")


if __name__ == "__main__":
    main()
