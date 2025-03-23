# vardorvis

Vardorvis is a custom Win32 CLI Tool that manages user input and program messages seamlessly, in support of optimal user experience. Allows user to navigate through previously issued commands.

## Features

- Command history navigation with up/down arrows
- Colored output and ASCII art
- Built-in commands (help, history, clear, exit)

## Set up your virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

## Installation

Download the python wheel from releases and run the command below.

```powershell
pip install vardorvis-0.1.0-py3-none-any.whl
```

## Usage

```powershell
vardorvis
```

## Available Commands

- `help` - Display help information
- `history` - Show command history
- `clear` - Clear the screen
- `exit` - Exit the CLI

## Requirements

- Python 3.8 or higher
- pywin32 (Windows only)


Below is a gif of the program run.

<img src="./README_Images/vardorvis_UI.gif" width="450" height="600">

**Figure 1.** *Vardorvis UI GIF.*

*ASCII art pulled from https://www.asciiart.eu/weapons/axes credit to Marcin Glinski*


End of file
