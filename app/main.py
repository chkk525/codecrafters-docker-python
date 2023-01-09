import os
import subprocess
import sys
import shutil
import tempfile

# This is a starting point for Python solutions to the "Build Your Own Docker" Challenge.

# In this challenge, you'll build a program that can pull an image from Docker Hub and execute commands in it.
# Along the way, we'll learn about chroot, kernel namespaces, the docker registry API and much more.

# Stage 4: Filesystem isolation
# In the previous stage, we executed a program that existed locally on our machine.
# This program had write access to the whole filesystem, which means that it could do dangerous things!
# In this stage, you'll use chroot to ensure that the program you execute doesn't have access to
# any files on the host machine.
# Create an empty temporary directory and chroot into it when executing the command.
# You'll need to copy the binary being executed too.


def main():
    # Create a temp dir
    temp_dir = tempfile.TemporaryDirectory()

    # Change the root dir of the currrent process to the temp dir
    os.chroot(temp_dir.name)

    # Copy the binary that is being executed to the dir
    shutil.copy(os.path.realpath(__file__), temp_dir.name)

    command = sys.argv[3]
    #  /usr/local/bin/docker-explorer
    args = sys.argv[4:]
    # ['exit', '29']

    # Run a command as a subprocess, capturing its output, and then printing the output to the console.
    completed_process = subprocess.run([command, *args], capture_output=True)

    # Wire stdout to sys.stdout/stderr to sys.stderr
    print(completed_process.stdout.decode("utf-8"), end='', file=sys.stdout)
    print(completed_process.stderr.decode("utf-8"), end='',  file=sys.stderr)

    # Return exit code if it is not equal to zero.
    if completed_process.returncode != 0:
        sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
