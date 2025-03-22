#!/usr/bin/env python3
import sys
import os
import threading
import queue
import msvcrt
import win32event
import win32con
import win32api
    
from typing import Optional

UP = 1
DOWN = -1


class VardorvisCLI:
    """Vardorvis Command Line Interface"""

    def __init__(self):
        """Initialize the CLI."""
        self.command_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.running = True
        self.prompt = "\033[1;91mvardorvis> \033[0m"  # Brighter red prompt (1;91m)
        self.current_input = ""
        self.command_event = threading.Event()
        self.shutdown_event = threading.Event()  # Event for graceful shutdown
        self.output_event = threading.Event()  # Event for output processing
        self.command_history = []  # List to store command history
        self.history_index = (
            0  # Current position in history (0 means not browsing history)
        )
        self.temp_input = (
            ""  # Temporary storage for current input when browsing history
        )

        # Create Windows event handle for recognizing when keyboard is pressed
        if os.name == "nt":
            self.stdin_handle = win32api.GetStdHandle(win32con.INPUT_KEYBOARD)
            self.input_event = win32event.CreateEvent(None, False, False, None)

        # Print ASCII art in bright red
        ascii_art = '''
                                        .g88888888888888888p.
                                      .d8888P""       ""Y8888b.
                                      "Y8P"               "Y8P'
                                         `.               ,'
                                           \\     .-.     /
                                            \\   (___)   /
 .------------------._______________________:__________j
/                   |                      |           |`-.,_
\\###################|######################|###########|,-'`
 `------------------'                       :    ___   l
                                            /   (   )   \\
                                           /     `-'     \\
                                         ,'               `.
                                      .d8b.               .d8b.
                                      "Y8888p..       ,.d8888P"
                                        "Y88888888888888888P"
                                           ""YY8888888PP"'''

        print("\033[1;91m" + ascii_art + "\033[0m\n")

    def clear_line(self):
        """Clear the current line in the terminal."""
        sys.stdout.write("\033[K")
        sys.stdout.flush()

    def move_cursor_to_start(self):
        """Move cursor to the start of the current line."""
        sys.stdout.write("\r")
        sys.stdout.flush()

    def navigate_history(self, direction: int):
        """Navigate through command history.
        direction: 1 for up, -1 for down so that history index will be between
        0 and -len(command_history) (always zero or negative).
        """
        if not self.command_history:  # Case where there is no history
            return

        if self.history_index == 0:  # Case where we are at the current input
            if direction == DOWN:
                return
            else:
                self.temp_input = self.current_input

        if abs(self.history_index) == len(self.command_history) and direction == UP:
            # Case where we are at the first command (bottom of history stack) and we are going up
            return

        if (
            self.history_index == -1 and direction == DOWN
        ):  # Case where we are going back to saved input
            self.current_input = self.temp_input
            self.history_index = 0
        else:
            # Case where we are somewhere in the middle of the history stack
            self.history_index = self.history_index - direction
            self.current_input = self.command_history[self.history_index]

        # Update display
        self.move_cursor_to_start()
        self.clear_line()
        sys.stdout.write(self.prompt + self.current_input)
        sys.stdout.flush()

    def handle_input(self):
        """Handle user input in a separate thread."""
        while self.running:
            try:
                # Get input without blocking
                if sys.stdin.isatty():
                    # Wait for input event
                    win32event.WaitForSingleObject(self.stdin_handle, 100)
                    if msvcrt.kbhit():
                        # Get first byte
                        first_byte = msvcrt.getch()
                        # Check if it's a special key (arrow keys start with 224)
                        if ord(first_byte) == 224:
                            # Get second byte
                            second_byte = msvcrt.getch()
                            if ord(second_byte) == 72:  # Up arrow
                                self.navigate_history(UP)
                                continue
                            elif ord(second_byte) == 80:  # Down arrow
                                self.navigate_history(DOWN)
                                continue
                            else:
                                continue  # Ignore other arrow keys
                        else:
                            try:
                                char = first_byte.decode("utf-8")
                                if char == "\r":  # Windows uses \r for Enter
                                    char = "\n"
                            except UnicodeDecodeError:
                                continue  # Ignore invalid UTF-8 sequences
                    else:
                        continue

                    if char == "\n":
                        # Process the command
                        command = self.current_input.strip()
                        if command:
                            self.command_queue.put(command)
                            self.command_event.set()  # Signal that a command is available
                            # Add to history if it's not empty and different from last command
                            if command and (
                                not self.command_history
                                or command != self.command_history[-1]
                            ):
                                self.command_history.append(command)
                            self.current_input = ""
                            self.history_index = 0  # Reset history index
                            self.temp_input = ""  # Clear temporary input
                            self.move_cursor_to_start()
                            self.clear_line()
                            sys.stdout.write(self.prompt + command + "\n")
                            sys.stdout.flush()
                    elif char == "\b":  # Backspace
                        if self.current_input:
                            self.current_input = self.current_input[:-1]
                            self.move_cursor_to_start()
                            self.clear_line()
                            sys.stdout.write(self.prompt + self.current_input)
                            sys.stdout.flush()
                    else:
                        self.current_input += char
                        sys.stdout.write(char)
                        sys.stdout.flush()
            except (OSError, IOError) as e:
                print(f"\nError handling input: {e}")
                break

    def print_output(self, message: str):
        """Print a message while preserving the prompt and current input."""
        # Move cursor to the start of the current line
        self.move_cursor_to_start()
        self.clear_line()

        # Print the message on a new line
        print(message)

        # Reprint prompt and current input
        sys.stdout.write(self.prompt + self.current_input)
        sys.stdout.flush()

    def process_output(self):
        """Process output messages in a separate thread."""
        while self.running:
            try:
                # Wait for output event
                if self.output_event.wait(timeout=0.1):
                    # Process all available output
                    while not self.output_queue.empty():
                        try:
                            message = self.output_queue.get_nowait()
                            self.print_output(message)
                        except queue.Empty:
                            break
                    self.output_event.clear()
            except (OSError, IOError) as e:
                print(f"\nError processing output: {e}")
                break

    def display_help(self):
        """Display help information about available commands."""
        help_text = """
Available commands:
    help    - Display this help message
    history - Display the command history
    exit    - Exit the CLI
    clear   - Clear the screen
    """
        self.print_output(help_text)

    def display_history(self):
        """Display the command history."""
        if not self.command_history:
            self.print_output("No command history available.")
            return

        history_text = "\nCommand History:"
        for i, cmd in enumerate(self.command_history, 1):
            history_text += f"\n    {i}. {cmd}"
        history_text += "\n"
        self.print_output(history_text)

    def process_command(self, command: str):
        """Process a command received from the user."""
        if command.lower() == "exit":
            self.running = False
            self.shutdown_event.set()  # Signal all threads to shut down
            self.print_output("Exiting...")
        elif command.lower() == "help":
            self.display_help()
        elif command.lower() == "clear":
            # Clear screen by printing ANSI escape sequence
            self.print_output("\033[2J\033[H")
        elif command.lower() == "history":
            self.display_history()
        else:
            self.print_output(f"Received command: {command}")

    def send_message(self, message: str):
        """Send a message to be displayed in the CLI."""
        self.output_queue.put(message)
        self.output_event.set()  # Signal that output is available

    def start(self):
        """Start the CLI interface."""
        # Set up input/output handling
        input_thread = threading.Thread(target=self.handle_input)
        output_thread = threading.Thread(target=self.process_output)

        # Start threads
        input_thread.daemon = True
        output_thread.daemon = True
        input_thread.start()
        output_thread.start()

        # Print initial prompt
        sys.stdout.write(self.prompt)
        sys.stdout.flush()

        try:
            while self.running:
                # Wait for command event or shutdown
                if self.shutdown_event.wait(timeout=0.1):
                    break
                if self.command_event.wait(timeout=0.1):
                    # Process all available commands
                    while not self.command_queue.empty():
                        try:
                            command = self.command_queue.get_nowait()
                            self.process_command(command)
                        except queue.Empty:
                            break

                    # Reset event
                    self.command_event.clear()

        except KeyboardInterrupt:
            self.running = False
            self.shutdown_event.set()  # Signal all threads to shut down
            print("\nShutting down...")


def main():
    try:
        cli = VardorvisCLI()
        cli.start()
    except (OSError, IOError) as e:
        print(f"Error starting CLI: {e}")
    except KeyboardInterrupt:
        print("\nCLI terminated by user.")
    except ImportError as e:
        print(f"Required modules not found: {e}")
        print("Please ensure all required modules are installed.")


if __name__ == "__main__":
    main()
