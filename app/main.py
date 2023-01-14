import ctypes
import subprocess
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from urllib.parse import urlencode
import json


def copy_file_to_dir(file_path, target_dir):
    """
    Copy the file from the provided file path to the target directory.
    The directory structure of the file path will be created in the target directory.

    Args:
        file_path (str): The path of the file to be copied.
        target_dir (str): The path of the target directory.

    Raises:
        Exception: If the provided file path is not a valid file or the target directory does not exist
    """
    # Check if the provided file path is a valid file
    if not os.path.isfile(file_path):
        raise Exception('No executable found at the provided file path')
    if not os.path.isdir(target_dir):
        raise Exception('Target dir does not exist')
    # Create the same directory structure in the target directory
    path_in_dir = os.path.join(
        target_dir,
        os.path.dirname(file_path).strip('/')
    )
    os.makedirs(path_in_dir)

    # Copy the file to the target directory
    shutil.copy(file_path, os.path.join(
        path_in_dir, os.path.basename(file_path)))


def decode_response_and_parse_to_json(response):
    """
    Parse the response content to json object

    Args:
        response (http.client.HTTPResponse): The response object to be parsed.

    Returns:
        dict: Json object of the response content.
    """
    return json.loads(response.read().decode('utf-8'))


def get_token(auth_realm, image_name):
    """
    Get token from auth_realm with the required scope for image_name

    Args:
        auth_realm (str): The authentication realm.
        image_name (str): The name of the image.

    Returns:
        str: Token with the required scope for the image_name.
    """
    query_params = {
        'service': 'registry.docker.io',
        'scope': f"repository:library/{image_name}:pull"
    }
    url = f"{auth_realm}?{urlencode(query_params)}"
    auth_request = urllib.request.Request(url)

    with urllib.request.urlopen(auth_request) as auth_response:
        json_response = decode_response_and_parse_to_json(auth_response)
        token = json_response.get('token')
        return token


def get_manifest(image_name, image_tag, token):
    """
    Get the manifest for image_name and image_tag with token

    Args:
        image_name (str): The name of the image.
        image_tag (str): The tag of the image.
        token (str): The token with the required scope for the image.

    Returns:
        dict: The manifest for the image_name and image_tag.
    """
    registry_url = 'https://registry.hub.docker.com'
    manifest_url = f'{registry_url}/v2/library/{image_name}/manifests/{image_tag}'
    image_request = urllib.request.Request(manifest_url)
    image_request.add_header(
        'Authorization', f'Bearer {token}')

    with urllib.request.urlopen(image_request) as res2:
        manifest = json_response = decode_response_and_parse_to_json(
            res2)
        return manifest


def get_blobs(image_name, digests, token):
    """
    Get the blobs for image_name for each digest in digests with token

    Args:
        image_name (str): The name of the image.
        digests (list): List of digests for the image.
        token (str): The token with the required scope for the image.

    Returns:
        list: The blobs for the image_name for each digest in digests.
    """
    registry_url = 'https://registry.hub.docker.com'
    blobs = []
    for digest in digests:
        layer_url = f'{registry_url}/v2/library/{image_name}/blobs/{digest}'
        blob_request = urllib.request.Request(layer_url)
        blob_request.add_header(
            'Authorization', f'Bearer {token}')
        with urllib.request.urlopen(blob_request) as layer_res:
            blobs.append(layer_res.read())

    return blobs


def save_blobs(digests, blobs):
    """Save blobs to file with filename as digest[7:].tar"""
    filenames = []
    for digest, blob in zip(digests, blobs):
        filename = f'{digest[7:]}.tar'
        filenames.append(filename)
        with open(filename, 'wb') as file:
            file.write(blob)
    return filenames


def extract_and_remove_tars(filenames, target_dir):
    """
    Extract all files from tar files in the list of filenames to the target directory.
    Then remove the tar files

    Args:
        filenames (list): A list of filenames of tar files.
        target_dir (str): The path of the target directory.

    Raises:
        Exception: If the target directory does not exist.
    """
    if not os.path.isdir(target_dir):
        raise Exception('Target dir does not exist')
    for filename in filenames:
        with tarfile.open(filename, "r") as tar:
            tar.extractall(path=target_dir, members=tar.getmembers())
        os.remove(filename)


def download_image(target_dir, image_name, image_tag=None):
    """
    Download the image and extract its layers to the target directory.

    Args:
        target_dir (str): The path of the target directory.
        image_name (str): The name of the image.
        image_tag (str, optional): The tag of the image. Defaults to None.

    Raises:
        Exception: If the target directory does not exist.
    """
    if image_name is None:
        raise Exception
    if image_tag is None:
        image_tag = 'latest'
    if not os.path.isdir(target_dir):
        raise Exception('Target dir does not exist')

    # Attempt to begin a pull operation with the registry.
    try:
        manifest_url = f'https://registry.hub.docker.com/v2/library/{image_name}/manifests/{image_tag}'
        response = urllib.request.urlopen(manifest_url)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            # Get the auth server url from the response header
            auth_header_str = e.headers.get('WWW-Authenticate')
            if auth_header_str:
                auth_headers = {}
                for ele in auth_header_str.split(','):
                    k, v = ele.split('=')
                    auth_headers[k.lower()] = v.replace('"', '')

                auth_realm = auth_headers['bearer realm']
                token = get_token(auth_realm, image_name)
                manifest = get_manifest(image_name, image_tag, token)
                digests = [layer['blobSum'] for layer in manifest['fsLayers']]
                blobs = get_blobs(image_name, digests, token)
                filenames = save_blobs(digests, blobs)
                extract_and_remove_tars(filenames, target_dir)


def main():
    # Get the command and its arguments from the command line
    image_name = sys.argv[2]
    command, *args = sys.argv[3:]

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the executable file to the temporary directory
        copy_file_to_dir(command, temp_dir)

        # Use ctypes library to call syscall to create a new process namespace
        unshare = 272
        clone_new_pid = 0x20000000
        # loads the C library libc which is the standard C library that provides the system call interface on Linux systems.
        libc = ctypes.CDLL(None)
        libc.syscall(unshare, clone_new_pid)

        # Download image to temp_dir
        download_image(temp_dir, image_name)

        # Change the root directory to temp_dir
        os.chroot(temp_dir)

        # Run the command in the new namespace
        completed_process = subprocess.run([command, *args])

        # Exit the program with the return code of the command
        sys.exit(completed_process.returncode)


if __name__ == '__main__':
    main()
