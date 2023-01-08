import subprocess
import sys

# This is a starting point for Python solutions to the "Build Your Own Docker" Challenge.

# In this challenge, you'll build a program that can pull an image from Docker Hub and execute commands in it.
# Along the way, we'll learn about chroot, kernel namespaces, the docker registry API and much more.


# Stage 2: Wireup stdout & stderr
# You'll now pipe the program's stdout and stderr to the parent process.
# Like the last stage, the tester will run your program like this:
# mydocker run ubuntu:latest /usr/local/bin/docker-explorer echo hey
# To test this behaviour locally, you could use the echo + echo_stderr commands that docker-explorer exposes. Run docker-explorer --help to view usage.

# Usage: docker-explorer COMMAND [ARGS]

# Commands:
#   echo <something>        : prints <something> to stdour
#   echo_stderr <something> : prints <something> to stderr
#   mypid                   : prints the process's PID
#   ls <dir>                : lists files in <dir>
#   touch <path>            : create a new file at <path>
#   exit <exit_code>        : exit with <exit_code>

# Examples:
#   docker-explorer echo hey
#   docker-explorer ls /

# If you've got any logs or print statements in your code, make sure to remove them. The tester can't differentiate between debug logs and the actual output!


def main():
    command = sys.argv[3]
    args = sys.argv[4:]

    # Run a command as a subprocess, capturing its output, and then printing the output to the console.
    completed_process = subprocess.run([command, *args], capture_output=True)

    # Wire stdout to sys.stdout/stderr to sys.stderr
    print(completed_process.stdout.decode("utf-8"), end='', file=sys.stdout)
    print(completed_process.stderr.decode("utf-8"), end='',  file=sys.stderr)


if __name__ == "__main__":
    main()
