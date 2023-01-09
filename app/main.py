import os
import shutil
import tempfile
import sys
import subprocess

# This is a starting point for Python solutions to the "Build Your Own Docker" Challenge.

# In this challenge, you'll build a program that can pull an image from Docker Hub and execute commands in it.
# Along the way, we'll learn about chroot, kernel namespaces, the docker registry API and much more.

# Stage 5: Process isolation
# In the previous stage, we guarded against malicious activity by restricting an executable's access to the filesystem.
# There's another resource that needs to be guarded: the process tree.
# The process you're executing is currently capable of viewing all other processes running on the host system, and sending signals to them.
# In this stage, you'll use PID namespaces to ensure that the program you execute has its own isolated process tree.
# The process being executed must see itself as PID 1.


def main():
    # executable_file = '/usr/local/bin/docker-explorer'
    executable_file = sys.argv[3]
    args = sys.argv[4:]

    # Create a temp dir
    with tempfile.TemporaryDirectory() as temp_dir:
        # Remove first root
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
        p = subprocess.Popen(
            [f"./{bin_name}", *args], start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        # Read the output from the pipes
        stdout, stderr = p.communicate()

        # Wire stdout to sys.stdout/stderr to sys.stderr
        print(stdout.decode(
            "utf-8"), end='', file=sys.stdout)
        print(stderr.decode(
            "utf-8"), end='',  file=sys.stderr)

        # Return exit code if it is not equal to zero.
        if p.returncode != 0:
            sys.exit(p.returncode)


if __name__ == "__main__":
    main()
