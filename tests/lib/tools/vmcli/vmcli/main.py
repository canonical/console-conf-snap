# Copyright (C) 2024 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# A tool for interacting with QEMU VM over a telnet connection to the QEMU's
# monitor interface.

import argparse
import asyncio
import asyncio.exceptions
import logging
import pathlib

import telnetlib3
import telnetlib3.client

log = logging.getLogger("main")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="tool for interacting with QEMU VM")
    parser.add_argument(
        "--monitor", default="localhost:8888", help="QEMU monitor address"
    )
    sub = parser.add_subparsers(required=True)
    screen = sub.add_parser("screenshot", help="take screenshot")
    screen.add_argument("--output", required=True)
    screen.set_defaults(cmd="screenshot")

    send_input = sub.add_parser("send-input", help="inject keyboard input")
    send_input.add_argument(
        "--raw",
        help="raw qemu monitor key sequence, eg. 'ctrl-alt-f1'",
        action="store_true",
        default=False,
    )
    send_input.add_argument(
        "what",
        help="input to send, newlines can be encoded as \n or simply a newline character",
    )
    send_input.set_defaults(cmd="input")

    reboot = sub.add_parser("reboot", help="reboot the system")
    reboot.set_defaults(cmd="reboot")

    return parser.parse_args()


async def send_input(what: str, addr: str, raw: bool = False) -> None:
    host, port = addr.split(":")

    special = {
        ".": "dot",
        "\n": "kp_enter",
        "@": "shift-2",
    }

    if raw:
        qemu_sequence = [what]
    else:
        qemu_sequence = []
        escaped = False
        for c in what:
            if not escaped:
                if c == "\\":
                    escaped = True
                    continue
                if c in special:
                    qemu_sequence.append(special[c])
                elif c.isalnum() and c.islower():
                    qemu_sequence.append(c)
                elif c.isalnum() and c.isupper():
                    qemu_sequence.append(f"shift-{c}")
                else:
                    raise RuntimeError(f"character '{c}' is not supported")
            else:
                if c == "n":
                    qemu_sequence.append("kp_enter")
                else:
                    raise RuntimeError(f"unsupported escape sequence \\{c}")

    log.debug("qemu sequence: %s", qemu_sequence)

    async def _send_input(
        reader: telnetlib3.TelnetReader, writer: telnetlib3.TelnetWriter
    ) -> None:
        log.debug("ready to send input")
        d = await reader.read(256)
        log.debug("got data: %s", d)

        # actual key sequence we need to process
        for k in qemu_sequence:
            cmd = f"sendkey {k}\n"
            log.debug("sending '%s'", cmd)
            try:
                writer.write(cmd)
            except:
                log.exception("failed write")
                raise

            try:
                d = await reader.read(256)
                log.debug("got data: %s", d)
                log.debug("failed???")
            except asyncio.exceptions.CancelledError:
                log.debug("read canceled")
            except:
                log.exception("failed")
                raise

        writer.write_eof()

    await telnetlib3.client.open_connection(host=host, port=port, shell=_send_input)


async def screenshot(output: str, addr: str) -> None:
    host, port = addr.split(":")
    log.debug("connect to %s:%s", host, port)

    outputp = pathlib.Path(output)
    if not outputp.is_absolute():
        outputp = pathlib.Path.cwd() / outputp
    log.debug("save to %s", str(outputp))

    async def _screenshot(
        reader: telnetlib3.TelnetReader, writer: telnetlib3.TelnetWriter
    ) -> None:
        log.debug("ready to screen dump")
        d = await reader.readline()
        log.debug("data: %s", d)
        cmd = f"screendump {outputp}\n"
        log.debug("command: '%s'", cmd)
        writer.write(cmd)
        writer.write_eof()

    await telnetlib3.client.open_connection(host=host, port=port, shell=_screenshot)


async def reboot(addr: str) -> None:
    host, port = addr.split(":")
    log.debug("connect to %s:%s", host, port)

    async def _reboot(
        reader: telnetlib3.TelnetReader, writer: telnetlib3.TelnetWriter
    ) -> None:
        d = await reader.readline()
        log.debug("data: %s", d)
        writer.write("system_reset\n")
        writer.write_eof()

    await telnetlib3.client.open_connection(host=host, port=port, shell=_reboot)


def main() -> None:
    args = parse_arguments()
    logging.basicConfig(level=logging.DEBUG)

    if args.cmd == "screenshot":
        asyncio.run(screenshot(args.output, addr=args.monitor))
    elif args.cmd == "input":
        asyncio.run(send_input(args.what, addr=args.monitor, raw=args.raw))
    elif args.cmd == "reboot":
        asyncio.run(reboot(addr=args.monitor))
