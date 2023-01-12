import os
import shutil
import tempfile
import sys
import subprocess
import urllib.request
import pathlib
import atexit

# This is a starting point for Python solutions to the "Build Your Own Docker" Challenge.

# In this challenge, you'll build a program that can pull an image from Docker Hub and execute commands in it.
# Along the way, we'll learn about chroot, kernel namespaces, the docker registry API and much more.

# Stage 5: Process isolation
# In the previous stage, we guarded against malicious activity by restricting an executable's access to the filesystem.
# There's another resource that needs to be guarded: the process tree.
# The process you're executing is currently capable of viewing all other processes running on the host system, and sending signals to them.
# In this stage, you'll use PID namespaces to ensure that the program you execute has its own isolated process tree.
# The process being executed must see itself as PID 1.

# Step6: Fetch an image from the Docker Registry
# In this stage, you'll use the Docker registry API to fetch the contents of a
# public image on Docker Hub and then execute a command within it.
# You'll need to:
# Do a small authentication dance
# Fetch the image manifest
# Pull layers of an image and extract them to the chroot directory
# The base URL for Docker Hub's public registry is registry.hub.docker.com.
# The tester will run your program like this:
# mydocker run ubuntu:latest /bin/echo hey
# The image used will be an official image from Docker Hub. For example: alpine:latest, ubuntu:latest, busybox:latest. When interacting with the Registry API, you'll need to prepend library/ to the image names.


def get_image(image):
    repo = f"library/{image}"
    url = f"https://registry.hub.docker.com:3200/v2/{repo}/"
    print(url)
    with urllib.request.urlopen(url) as response:
        print(response)


def copy_executable_in_directory(executable_path, target_dir):
    if not os.path.isfile(executable_path):
        raise Exception('No executable')

    executable_file_name = os.path.basename(executable_path)
    executable_path_inside_dir = pathlib.Path(
        os.path.join(target_dir, executable_file_name))
    shutil.copy(executable_path, executable_path_inside_dir)


def main():
    command, *args = sys.argv[3:]

    if not os.path.isfile(command):
        print(f"The command {command} doesn't exist")
        sys.exit(1)

    # Create temp dir
    try:
        temp_dir = tempfile.mkdtemp()
    except Exception as e:
        print(f"Unable to create temp directory: {e}")
        sys.exit(1)

    # Spawn child process
    try:
        cpid = os.fork()
        if cpid == 0:
            # Copy executable to temp dir and chroot and move to the dir.
            copy_executable_in_directory(command, temp_dir)
            os.chroot(temp_dir)
            os.chdir('/')
            # Run the copied executable as subprocess
            command = os.path.join('/', os.path.basename(command))

            command_to_run = ['unshare', '--pid',
                              '--fork' '--mount-proc'] + [command, *args]
            child_process = subprocess.Popen(
                command_to_run,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            stdout, stderr = child_process.communicate()
            # Wire stdout to sys.stdout/stderr to sys.stderr
            sys.stdout.buffer.write(stdout)
            sys.stderr.buffer.write(stderr)
            sys.exit(child_process.returncode)
    except Exception as e:
        print(f"Error occurred while trying to spawn child process: {e}")

    # os.waitpid() method is being used to wait for the child process to exit and retrieve its exit status.
    # The method returns a tuple containing the process ID of the child process
    # and the exit status of the child process.
    # The exit status is typically in the format of
    # status << 8 | exitcode
    # where status is the exit status of the process,
    # and exitcode is the low-order byte of the exit status.

    # To retrieve the exit code of the child process,
    # you need to perform a bitwise AND operation between the exit status and 0xFF (255 in decimal)
    #  to get the lower 8 bits which hold the exit code.
    _, child_exit_status = os.waitpid(cpid, 0)
    if args[0] == 'mypid':
        print(args, child_exit_status, os.WEXITSTATUS(child_exit_status))
    child_exit_code = os.WEXITSTATUS(child_exit_status)

    # Exit the parent process with the same return code as the child process
    sys.exit(child_exit_code)


if __name__ == "__main__":
    main()
