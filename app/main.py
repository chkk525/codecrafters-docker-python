import os
import shutil
import tempfile
import sys
import subprocess

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
    # executable_file = '/usr/local/bin/docker-explorer'
    executable_file = sys.argv[3]
    args = sys.argv[4:]

    # Create a temp dir
    with tempfile.TemporaryDirectory() as temp_dir:
        # # Remove first root
        components = executable_file.split(os.path.sep)
        # bin_name = os.path.sep.join(components[1:])
        bin_name = components[-1]
        new_executable_file = os.path.join(temp_dir, bin_name)

        # Copy the executable binary to temp_dir.
        shutil.copy(executable_file, new_executable_file)

        # Change the root dir and move to /.
        os.chroot(temp_dir)
        os.chdir('/')

        # Run sub.py as a subprocess along with command and args
        completed_process = subprocess.run(
            [f"./{bin_name}", *args], capture_output=True)

        # Wire stdout to sys.stdout/stderr to sys.stderr
        print(completed_process.stdout.decode(
            "utf-8"), end='', file=sys.stdout)
        print(completed_process.stderr.decode(
            "utf-8"), end='',  file=sys.stderr)

        # Return exit code if it is not equal to zero.
        if completed_process.returncode != 0:
            sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
