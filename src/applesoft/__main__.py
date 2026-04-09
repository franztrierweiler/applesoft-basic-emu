"""Point d'entrée : python -m applesoft."""

import argparse

from .debug import DebugTracer
from .io_cli import IOBridgeCLI
from .repl import REPL


def main() -> None:
    parser = argparse.ArgumentParser(description="Émulateur Applesoft BASIC")
    parser.add_argument("--debug", action="store_true", help="Activer le mode debug")
    args = parser.parse_args()

    io = IOBridgeCLI()
    debug = DebugTracer()
    if args.debug:
        debug.enable()
    repl = REPL(io, debug=debug)
    repl.run()


if __name__ == "__main__":
    main()
