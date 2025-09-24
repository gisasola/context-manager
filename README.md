# Simple Context Manager

This is a simple application to manage contexts, which are lists of URLs and file paths. You can create, save, load, edit, and open contexts.

## How it works

The application is built with Python and Tkinter. It allows you to manage collections of URLs and local file paths, which are saved as JSON files.

### Main Features

- **Create a new context**: You can create a new list of items (URLs or file paths).
- **Save a context**: The list of items can be saved to a JSON file.
- **Load a context**: You can load a previously saved context from a JSON file.
- **Edit a context**: You can add or remove items from a loaded context.
- **Open a context**: This will open all the URLs in your default web browser and all the files with their default application.

### File Structure

- `context_manager.py`: The main Python script that contains all the application logic and UI.
- `*.json`: These files, stored by default in `~/Documents/Contexts`, contain the contexts you save.

## How to Use

1.  **Run the application**: Execute the `context_manager.py` script.
2.  **Welcome Screen**:
    - **Load Context**: Select a context from the list and click this button to load and open it.
    - **Edit Context**: Select a context to modify it.
    - **Add missing**: Browse for a context file that is not in the default directory.
    - **Create New Context**: Go to the creation screen to start a new context.
3.  **Create/Edit Screen**:
    - Use the `+` button to add a new URL or file path.
    - Use the `–` button to remove selected items.
    - Click `Save Context` or `Save Changes` to store your context.
4.  **Settings**:
    - You can change the default directory where contexts are saved via the `Settings` menu.

This tool is useful for grouping together various resources related to a specific task or project, allowing you to quickly open them all at once.
