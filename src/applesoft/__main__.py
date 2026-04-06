"""Point d'entrée : python -m applesoft."""

from .io_cli import IOBridgeCLI
from .repl import REPL


def main() -> None:
    io = IOBridgeCLI()
    repl = REPL(io)
    repl.run()


if __name__ == "__main__":
    main()
