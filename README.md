# CNext Wind AI

Th is part of a project that aims to use ChatGPT to control fans placed under a cloth in an art exhibition. The fans' intensity output is determined based on the value assigned to each word in the prompt. The server code is responsible for handling client connections, receiving prompts from clients, generating responses using ChatGPT, and outputting the fan intensity based on the output.

### ChatGPT and Fan Intensity Control

The core idea of the project is to use ChatGPT to control the intensity of fans placed under a cloth in an art exhibition. The server code facilitates this control by receiving prompts from clients, passing them to ChatGPT (via API) for generating responses, and determining the fan intensity based on the output.

When a client sends a prompt to the server, the server code uses the `get_completion` function to generate a completion response using ChatGPT. The response represents the words that ChatGPT generates based on the prompt.

The server then creates values for each word in the answer by instructing ChatGPT to generate a JSON text containing intensity scores corresponding to the amount of change caused by replacing words with their antonyms.

The server then attempts to parse the response words as JSON. If successful, it assumes that the response contains intensity values for the fans. The server extracts the parsed JSON data and uses it to control the fan intensity accordingly.

In case the parsing fails or the output is `None`, indicating an unsuccessful ChatGPT response, the server falls back to generating random intensity values using the `random_values` function. This ensures that the fans will continue to operate even if ChatGPT fails to provide meaningful intensity values.

## Code Structure

The server code consists of two main files: `server.py` and `server_utils.py`. Here's a brief explanation of the functionality:

### `server.py`

This file contains the main code for the server. It performs the following steps:

1. It accepts the arguments  `--port` (specifying the port for the socket) and `--verbose_level` (specifying the logger level).
2. Creates a TCP socket server using `socket.socket` with IPv4 addressing and TCP protocol.
3. Sets socket options to reuse the address and binds the server socket to listen on all available IP addresses (`0.0.0.0`) and the specified port.
4. Starts listening for incoming client connections using `socket.listen`.
5. Enters an infinite loop to handle multiple client connections.
6. Within the loop, it waits for a client to connect using `socket.accept`.
7. Receives a prompt from the client using the `recv_end` function from `wind_ai.utils.server_utils`.
8. If the received prompt is not empty, it generates a completion response using the `get_completion` function from `wind_ai.utils.server_utils` and extracts the response words using `get_json`.
9. Tries to parse the response words as JSON. If successful, it sets the `output` variable with the parsed JSON data. If parsing fails, it retries the parsing with a different temperature value (0.5) by calling `get_json` again.
10. If the parsing is still unsuccessful or the `output` variable is `None`, it logs a debug message and generates random intensity values using the `random_values` function from `wind_ai.utils.server_utils`.
11. Catches specific exceptions (`BrokenPipeError`, `JSONDecodeError`) and logs appropriate error messages.
12. Logs a message when a client disconnects.
13. Catches a `KeyboardInterrupt` to exit the server.
14. Shuts down the server socket and closes the connection.
15. Logs a message when the host is closed.

### `server_utils.py`

It serves as a utility module for the server code. The code structure and functionality are the same as explained above.

## Usage

To run the server, execute the `server.py`  file in a Python environment. You can pass command-line arguments to customize the server behavior, such as the port number and logger level. The default port is set to `9000`, and the default logger level is set to `info`. Here's an example command to run the server:

`python server.py --port 9000 --verbose_level debug`

Once the server is running, clients can connect to it and send prompts. The server will generate ChatGPT responses, parse them for intensity values, and control the fan intensity accordingly.
