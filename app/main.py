import subprocess
import sys

# This is a starting point for Python solutions to the "Build Your Own Docker" Challenge.

# In this challenge, you'll build a program that can pull an image from Docker Hub and execute commands in it.
# Along the way, we'll learn about chroot, kernel namespaces, the docker registry API and much more.


# Stage 3: Handle exit codes
# In this stage, you'll need to relay the program's exit code to the parent process.
# If the program you're executing exits with exit code 1, your program should exit with exit code 1 too.
# To test this behaviour locally, you could use the exit command that docker-explorer exposes. Run docker-explorer --help to view usage.
# Just like the previous stage, the tester will run your program like this:
# mydocker run ubuntu:latest /usr/local/bin/docker-explorer exit 1

def main():
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
