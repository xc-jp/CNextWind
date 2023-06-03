import argparse
import json
import logging
import socket
import traceback
from typing import Literal

import hbtools

from wind_ai.utils.server_utils import get_completion, get_json, random_values, recv_end


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=9000, help="Port for the socket")
    parser.add_argument("--verbose_level", "-v", choices=["debug", "info", "error"], default="info", type=str,
                        help="Logger level.")
    args = parser.parse_args()

    port: int = args.port
    verbose_level: Literal["debug", "info", "error"] = args.verbose_level

    logger = hbtools.create_logger("WindAI Server", verbose_level=verbose_level)

    # Creating TCP socket server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", port))  # noqa: S104  # listening for any incoming IP
    server_socket.listen(5)

    try:
        while True:
            try:
                while True:  # keep receiving and sending message while client connected
                    logger.info(f"Listen for client on port {port}")
                    (_client_socket, client_address) = server_socket.accept()
                    logger.debug(f"Client connected at address {client_address}")

                    prompt = recv_end(server_socket)

                    if not prompt:  # recv return empty message if client disconnects
                        logger.debug("Message was empty")
                        break

                    response = get_completion(prompt)
                    words = get_json(response)
                    logging.debug(f"ChatGPT answer: {response}")

                    output: str | None = None
                    for _ in range(2):
                        try:
                            output = json.loads(words)
                            logging.debug(f"ChatGPT json output: {output}")
                            break
                        except json.decoder.JSONDecodeError:
                            words = get_json(response, temperature=0.5)  # Retry with different temperature
                    if output is None:
                        logging.debug("ChatGPT failed, using random.")
                        output = random_values()  # Generate random intensity values if parsing fails

            except (BrokenPipeError, json.decoder.JSONDecodeError):
                logger.exception("Could not decode json")
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
