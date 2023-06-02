import argparse
import logging
import traceback
import json
import socket
from typing import Literal

import hbtools

# from wind_ai.utils.server_utils import get_json, get_completion, random_values
from .utils.server_utils import get_json, get_completion, random_values



def recv_end(listening_socket: socket.socket, end: str = "<EOF>", buffer_size: int = 4096) -> str:
    """Receive data from the given socket until the socket disconnects or the end message signal is received.

    Args:
        listening_socket: The socket to listen to.
        end: The end string that signals that the message has been received in its entirety.
        buffer_size: Buffer to use for the socket.

    Returns:
        The data received from the socket, as a utf-8 string.
    """
    end_bytes = end.encode()
    total_data: list[bytes] = []
    data = ""
    while True:
        data = listening_socket.recv(buffer_size)
        if not data:  # recv return empty message if client disconnects
            return data.decode("utf-8")
        if end_bytes in data:
            total_data.append(data[:data.find(end_bytes)])
            break
        total_data.append(data)
        if len(total_data) > 1:
            # check if end_of_data was split
            last_pair = total_data[-2] + total_data[-1]
            if end_bytes in last_pair:
                total_data[-2] = last_pair[:last_pair.find(end_bytes)]
                total_data.pop()
                break
    return b"".join(total_data).decode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=9000, help="Port for the socket")
    parser.add_argument("--verbose_level", "-v", choices=["debug", "info", "error"], default="info", type=str,
                        help="Logger level.")
    args = parser.parse_args()

    port: int = args.port
    verbose_level: Literal["debug", "info", "error"] = args.verbose_level

    logger = hbtools.create_logger("PickingEngine", verbose_level=verbose_level)

    # Creating TCP socket server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", port))  # listening for any incoming IP
    server_socket.listen(5)

    try:
        while True:
            try:
                while True:  # keep receiving and sending message while client connected
                    logger.info("Listen for client on port {}".format(port))
                    (_client_socket, client_address) = server_socket.accept()
                    logger.debug("Client connected at address {}".format(client_address))

                    prompt = recv_end(server_socket)

                    if not prompt:  # recv return empty message if client disconnects
                        logger.debug("Message was empty")
                        break

                    response = get_completion(prompt)
                    words = get_json(response)
                    logging.debug(f"ChatGPT answer: {response}")

                    output: dict[str, dict[str, float]] | None = None
                    for _ in range(2):
                        try:
                            output = json.loads(words)
                            logging.debug(f"ChatGPT json output: {output}")
                            break
                        except json.decoder.JSONDecodeError:
                            words = get_json(response, temperature=0.5)  # Retry with different temperature
                    if output is None:
                        logging.debug(f"ChatGPT failed, using random.")
                        output = random_values()  # Generate random intensity values if parsing fails

            except (BrokenPipeError, json.decoder.JSONDecodeError):
                logger.error("Could not decode json", exc_info=True)
                pass
            except Exception:
                logger.exception(traceback.format_exc())
            logger.info("Client disconnected")
    except KeyboardInterrupt:
        logger.debug("KeyboardInterrupt, exiting.")
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
    logger.info("Host closed.")


if __name__ == "__main__":
    main()
