# Remote Mouse and Keyboard Controller

This project allows you to control your computer's mouse and keyboard remotely using a web interface.  It consists of a Python server built with Flask and a simple HTML frontend.  The server provides endpoints for controlling the mouse cursor, simulating clicks, typing text, and even shutting down the server.  A QR code is generated for easy access from a mobile device.
![image](https://github.com/user-attachments/assets/090af24e-e630-4dc3-a583-dab0c4c23105)



## Features

*   **Remote Mouse Control:** Move the mouse cursor with relative or absolute positioning. Includes adaptive smoothing and speed control for improved precision.
*   **Click Simulation:** Simulate left, middle, or right mouse clicks.
*   **Text Input:** Type text on the computer using a virtual keyboard. Supports special keys like backspace and enter.
*   **QR Code Access:**  Generates a QR code to quickly access the web interface on a mobile device.
*   **Network Check:** Provides a network check endpoint to verify connectivity between the client and server.
*   **Kill Switch:** A kill switch endpoint to remotely shut down the server.
  ![image](https://github.com/user-attachments/assets/73585eb1-50a3-4b14-87b2-f76c67b04f13)


## Requirements

*   Python 3.6+
*   Flask
*   Flask-CORS
*   PyAutoGUI
*   qrcode
*   socket
*   io
*   logging
*   os
*   signal
*   threading
*   time

You can install the necessary Python packages using pip:

pip install Flask Flask-CORS pyautogui qrcode


## Installation

1.  Clone the repository:

    ```
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  Install the dependencies (as mentioned in the Requirements section).

## Usage

1.  Run the `server.py` file:

    ```
    python server.py
    ```

2.  The server will start and print the local IP address and URL to access the web interface. It also displays a QR code in the console, which you can scan with your mobile device.

3.  Open the URL in your mobile device's browser.  Ensure your mobile device is on the same network as your computer.

4.  Use the web interface to control your mouse and keyboard.

## Code Structure

The project consists of the following files:

*   `server.py`: The main Flask application that handles routing and logic for controlling the mouse and keyboard.
*   `cursor_control.py`: Contains the `CursorController` class, which implements adaptive smoothing and speed control for mouse movements.
*   `index.html`: A simple HTML file serving as the user interface.

### `server.py`

This file contains the Flask application that defines the following routes:

*   `/`: Serves the `index.html` file.
*   `/qr`: Generates and serves a QR code as a PNG image.
*   `/move`: Handles mouse movement requests.  It receives x and y coordinates and moves the mouse accordingly, using the `CursorController` for smoothing and speed adjustments.
*   `/click`: Handles mouse click requests.  It receives the button type (left, middle, right) and simulates a click.
*   `/type`: Handles text input requests. It receives text and types it using `pyautogui`. It handles special keys like backspace and enter.
*   `/kill`:  Shuts down the server.
*   `/network-check`: Checks if the client and server are on the same network.

It also includes functions for:

*   `get_local_ip()`:  Gets the local IP address of the server.
*   `generate_qr_code()`: Generates a QR code for the server's URL.

### `cursor_control.py`

This file contains the `CursorController` class, which is responsible for:

*   Applying adaptive smoothing to mouse movements to reduce jitter.
*   Calculating adaptive speed based on movement magnitude for a more natural feel.

The `CursorController` class has the following methods:

*   `__init__()`: Initializes the cursor controller with base speed, min speed, max speed, and smoothing window parameters.
*   `apply_adaptive_smoothing(dx, dy)`: Applies adaptive smoothing based on movement velocity.
*   `calculate_adaptive_speed(dx, dy)`: Calculates speed based on movement magnitude.
*   `move_cursor(dx, dy, relative=True)`: Moves the cursor with improved precision.

### `index.html`

A basic HTML file that provides a minimal user interface with buttons for actions like right click and opening a keyboard interface (implementation for these actions would need to be added with javascript to send requests to the Flask server).  It also includes a network connection check.



## Network Configuration

Make sure your computer and mobile device are connected to the same network. If you are using a firewall, ensure that port 5000 is open.

The application performs a basic network check to determine if the client and server are on the same subnet. However, more complex network configurations might require additional setup.

## Kill Switch

The `/kill` endpoint provides a kill switch to remotely shut down the server. This can be useful if you need to stop the server from your mobile device.

## Debugging

*   Check if your phone and computer are on the same network.
*   Make sure no firewall is blocking port 5000.
*   Try accessing the URL in your phone's browser.
*   Enable debug mode in the Flask app for more detailed error messages.

## Future Enhancements

*   Implement a more sophisticated web interface with a virtual keyboard and mouse controls.
*   Add support for scrolling.
*   Implement screen mirroring.
*   Improve network connectivity and error handling.
*   Add security features such as authentication.
