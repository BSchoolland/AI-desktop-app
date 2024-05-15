import subprocess
import threading
import queue
import os

class ShellSession:
    def __init__(self):
        self.process = subprocess.Popen(
            ['/bin/bash'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            bufsize=1,
            universal_newlines=True
        )
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.stdout_thread = threading.Thread(target=self._enqueue_output, args=(self.process.stdout, self.stdout_queue))
        self.stderr_thread = threading.Thread(target=self._enqueue_output, args=(self.process.stderr, self.stderr_queue))
        self.stdout_thread.daemon = True
        self.stderr_thread.daemon = True
        self.stdout_thread.start()
        self.stderr_thread.start()

    def _enqueue_output(self, out, queue):
        for line in iter(out.readline, ''):
            queue.put(line)
        out.close()

    def get_prompt(self):
        # Retrieve the current username and hostname
        user = os.getenv("USER")
        hostname = os.getenv("HOSTNAME")
        # Run 'pwd' to get the current directory
        self.process.stdin.write('pwd\n')
        self.process.stdin.flush()
        current_dir = ''
        while True:
            line = self.stdout_queue.get(timeout=1)
            if line.strip() != '':
                current_dir = line.strip()
                break
        # Format similar to a typical bash prompt
        return f"{user}@{hostname}:{current_dir}$ "

    def run_command(self, command):
        prompt = self.get_prompt()
        # Print the prompt and the command
        print(prompt + command)
        # Send the command to the shell
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()
        
        # Read the output until we detect the next prompt
        output = []
        while True:
            try:
                line = self.stdout_queue.get(timeout=1)
                if line.strip() == command:  # Ignore the echo of the command
                    continue
                if line.strip().endswith('$ '):  # Assuming a prompt ends with '$ '
                    break
                output.append(line)
            except queue.Empty:
                break

        # Check for any errors
        errors = []
        while True:
            try:
                error_line = self.stderr_queue.get_nowait()
                errors.append(error_line)
            except queue.Empty:
                break

        if errors:
            return ''.join(errors)
        return ''.join(output)

    def close(self):
        # Close the process
        self.process.stdin.write('exit\n')
        self.process.stdin.flush()
        self.process.terminate()
        self.process.wait()

# Sample usage
if __name__ == '__main__':
    shell = ShellSession()
    print(shell.run_command('ls'))
    shell.close()
