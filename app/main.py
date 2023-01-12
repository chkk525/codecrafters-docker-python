import ctypes
import subprocess
import os
import shutil
import sys
import tempfile


def copy_file_to_dir(file_path, target_dir):
    # Check if the provided file path is a valid file
    if not os.path.isfile(file_path):
        raise Exception('No executable found at the provided file path')

    # Create the same directory structure in the target directory
    path_in_dir = os.path.join(
        target_dir,
        os.path.dirname(file_path).strip('/')
    )
    os.makedirs(path_in_dir)

    # Copy the file to the target directory
    shutil.copy(file_path, os.path.join(
        path_in_dir, os.path.basename(file_path)))


def main():
    # Get the command and its arguments from the command line
    command, *args = sys.argv[3:]

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the executable file to the temporary directory
        copy_file_to_dir(command, temp_dir)

        # Use ctypes library to call syscall to create a new process namespace
        # defining the system call number of the unshare syscall.
        unshare = 272
        # flag that tells the unshare syscall to create a new PID namespace.
        # equivalent to 536870912 in decimal.
        clone_new_pid = 0x20000000
        # loads the C library libc which is the standard C library that provides the system call interface on Linux systems.
        libc = ctypes.CDLL(None)
        libc.syscall(unshare, clone_new_pid)

        # Change the root directory to the temporary directory
        os.chroot(temp_dir)

        # Run the command in the new namespace
        completed_process = subprocess.run([command, *args])

        # Exit the program with the return code of the command
        sys.exit(completed_process.returncode)


if __name__ == '__main__':
    main()
