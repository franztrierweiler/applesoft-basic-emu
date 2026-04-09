"""IOBridgeWeb — Brython-based IOBridge implementation for the web interface.

All DOM and browser interactions are confined to this module (RG-0014, SEC-TECH-11).
Security: uses textContent exclusively, never inner-HTML (SEC-DEV-03, SEC-TECH-12).
Time-slicing: uses YieldSignal/InputRequestSignal + setTimeout for non-blocking
execution (ADR-003, RG-0015).
"""

# -- Brython imports (confined to this module — CA-UC-025-10) --
from browser import document, html, window, timer  # noqa: F401

# -- Core emulator imports --
# These will work when Brython resolves the Python path to src/applesoft/
# The path must be set up via brython({pythonpath: [...]}) in index.html.


# ---------------------------------------------------------------------------
# IOBridgeWeb — implements the IOBridge protocol for the browser
# ---------------------------------------------------------------------------
class IOBridgeWeb:
    """IOBridge implementation that renders to the browser DOM.

    Follows the IOBridge protocol defined in src/applesoft/io_bridge.py.
    Implements time-slicing runner for non-blocking program execution (RG-0015).
    """

    def __init__(self):
        self._interrupted = False
        self._cursor_column = 1
        self._video_mode = "normal"
        self._speed = 0
        self._last_key = 0
        self._console_output = document["console-output"]
        self._console_input = document["console-input"]
        self._console_prompt = document["console-prompt"]
        self._input_resolve = None  # Callback for async input
        self._key_resolve = None  # Callback for async get_char
        self._running = False  # True when a program is executing
        self._waiting_for_input = False  # True during INPUT/GET wait
        self._input_kind = None  # "input" or "get"
        self._input_resume_line = None
        self._input_resume_idx = None

        # Bind keyboard events for GET support and interrupt
        self._console_input.bind("keydown", self._on_keydown)
        # Capture Ctrl+C on the whole document (not just the input field)
        document.bind("keydown", self._on_document_keydown)

    # -- IOBridge protocol methods --

    def print_str(self, text):
        """Write text to the console DOM element.

        Uses textContent via createElement + textContent (SEC-DEV-03, SEC-TECH-12).
        Never uses inner-HTML.
        """
        if not text:
            return

        span = document.createElement("span")
        span.textContent = text
        self._console_output.appendChild(span)

        # Auto-scroll to bottom
        self._console_output.scrollTop = self._console_output.scrollHeight

        # Update cursor column tracking
        if "\n" in text:
            last_line = text.rsplit("\n", 1)[-1]
            self._cursor_column = len(last_line) + 1
        else:
            self._cursor_column += len(text)

    def input_str(self, prompt=""):
        """Display prompt and read a line of text from the user.

        In web mode, INPUT is handled asynchronously via InputRequestSignal.
        This method is kept for protocol compatibility but should not be called
        during program execution (the Interpreter raises InputRequestSignal instead).
        """
        if prompt:
            self.print_str(prompt)
        return ""

    def get_char(self):
        """Capture the next keyboard event.

        In web mode, GET is handled asynchronously via InputRequestSignal.
        This method is kept for protocol compatibility.
        """
        return ""

    def clear_screen(self):
        """Clear the console output."""
        # Remove all child nodes safely (no inner-HTML)
        while self._console_output.firstChild:
            self._console_output.removeChild(self._console_output.firstChild)
        self._cursor_column = 1

    def check_interrupt(self):
        """Check if an interrupt has been requested (STOP button or Ctrl+C)."""
        if self._interrupted:
            self._interrupted = False
            return True
        return False

    def set_interrupted(self):
        """Signal an interrupt (called by STOP button or Ctrl+C handler)."""
        self._interrupted = True

    def get_cursor_column(self):
        """Return the current cursor column (1-based)."""
        return self._cursor_column

    def set_video_mode(self, mode):
        """Set video mode: normal, inverse, flash."""
        self._video_mode = mode

    def set_speed(self, value):
        """Set character delay (0-255). Ignored in web for now."""
        self._speed = value

    def get_last_key(self):
        """Return the last key pressed (RG-0011, $C000)."""
        return self._last_key

    def set_last_key(self, key):
        """Set the last key pressed."""
        self._last_key = key

    def move_cursor_to_row(self, row):
        """Move cursor to row (no-op in web iteration 1)."""
        pass

    # -- Time-slicing runner (ADR-003, RG-0015) --

    def _run_program_sliced(self, command):
        """Run a BASIC command with time-slicing.

        Catches YieldSignal and InputRequestSignal to yield control
        to the browser between execution slices.
        """
        from applesoft.interpreter import YieldSignal, InputRequestSignal
        from applesoft.errors import BasicError

        self._running = True
        self._waiting_for_input = False

        try:
            self._repl._process_line(command)
        except YieldSignal as y:
            # Schedule next slice via setTimeout (yields to browser event loop)
            timer.set_timeout(lambda: self._resume_slice(y.line_num, y.stmt_idx), 0)
            return
        except InputRequestSignal as inp:
            # Wait for user input (keyboard event or input field)
            self._wait_for_async_input(inp)
            return
        except BasicError as e:
            self.print_str(e.format() + "\n")
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        self._finish_execution()

    def _resume_slice(self, line_num, stmt_idx):
        """Resume execution from a yield point (time-slicing).

        Called by setTimeout after a YieldSignal.
        """
        from applesoft.interpreter import YieldSignal, InputRequestSignal
        from applesoft.errors import BasicError

        if not self._running:
            self._finish_execution()
            return

        try:
            self._repl.interpreter.resume_execution(line_num, stmt_idx)
        except YieldSignal as y:
            timer.set_timeout(lambda: self._resume_slice(y.line_num, y.stmt_idx), 0)
            return
        except InputRequestSignal as inp:
            self._wait_for_async_input(inp)
            return
        except BasicError as e:
            self.print_str(e.format() + "\n")
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        self._finish_execution()

    def _wait_for_async_input(self, inp):
        """Enter async input wait state (INPUT or GET).

        Shows the input field for INPUT, or just waits for a keypress for GET.
        """
        self._waiting_for_input = True
        self._input_kind = inp.kind
        self._input_resume_line = inp.line_num
        self._input_resume_idx = inp.stmt_idx

        if inp.kind == "input":
            # Show input field and focus it
            self._console_input.value = ""
            self._console_input.focus()
        elif inp.kind == "get":
            # For GET, just wait for the next keypress
            self._console_input.focus()

    def _receive_input_value(self, value):
        """Process received input value and resume execution.

        Called when the user presses Enter (INPUT) or a key (GET).
        """
        from applesoft.interpreter import YieldSignal, InputRequestSignal
        from applesoft.errors import BasicError

        self._waiting_for_input = False
        line_num = self._input_resume_line
        stmt_idx = self._input_resume_idx

        try:
            self._repl.interpreter.resume_after_input(line_num, stmt_idx, value)
        except YieldSignal as y:
            timer.set_timeout(lambda: self._resume_slice(y.line_num, y.stmt_idx), 0)
            return
        except InputRequestSignal as inp:
            self._wait_for_async_input(inp)
            return
        except BasicError as e:
            self.print_str(e.format() + "\n")
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        self._finish_execution()

    def _finish_execution(self):
        """Clean up after program execution ends."""
        self._running = False
        self._waiting_for_input = False
        self.print_str("]")

    # -- Event handlers --

    def _on_document_keydown(self, event):
        """Handle keydown on the whole document (for Ctrl+C during execution)."""
        if event.key == "c" and event.ctrlKey:
            event.preventDefault()
            if self._running:
                self.set_interrupted()
                # If waiting for input, cancel the wait and finish
                if self._waiting_for_input:
                    self._waiting_for_input = False
                    self.print_str("^C\n")
                    self._running = False
                    self.print_str("]")

    def _on_keydown(self, event):
        """Handle keydown events on the console input field."""
        # Ctrl+C -> interrupt
        if event.key == "c" and event.ctrlKey:
            event.preventDefault()
            self.set_interrupted()
            if self._waiting_for_input:
                self._waiting_for_input = False
                self.print_str("^C\n")
                self._running = False
                self.print_str("]")
            return

        # Track last key for PEEK($C000)
        if len(event.key) == 1:
            self._last_key = ord(event.key.upper()) | 0x80  # Apple II convention

        # GET mode: capture single keypress (CA-UC-025-09)
        if self._waiting_for_input and self._input_kind == "get":
            if len(event.key) == 1:
                event.preventDefault()
                ch = event.key.upper()
                self.print_str(ch)
                self._receive_input_value(ch)
                return

        # Enter -> submit input line
        if event.key == "Enter":
            event.preventDefault()
            line = self._console_input.value
            self._console_input.value = ""

            # Echo the input to the console output
            self.print_str(line + "\n")

            # If waiting for INPUT, feed the value back to the interpreter
            if self._waiting_for_input and self._input_kind == "input":
                self._receive_input_value(line)
                return

            # Process the line through the REPL
            if hasattr(self, "_repl") and self._repl is not None:
                self._process_repl_line(line)

    def _process_repl_line(self, line):
        """Feed a line to the REPL for processing.

        Commands that start program execution (RUN, GOTO, GOSUB) are
        routed through the time-slicing runner. Other commands execute
        synchronously.
        """
        upper = line.strip().upper()

        # Commands that trigger program execution need time-slicing
        if upper.startswith("RUN") or upper.startswith("GOTO") or upper.startswith("GOSUB"):
            self._run_program_sliced(line)
            return

        # Regular REPL commands (LIST, NEW, DEL, etc.) run synchronously
        try:
            self._repl._process_line(line)
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        # Show prompt again
        self.print_str("]")

    # -- STOP button handler --

    def _on_stop_click(self, event):
        """Handle STOP button click (CA-UC-025-05).

        Sets the interrupt flag. During time-sliced execution, the interrupt
        will be checked at the start of the next slice.
        """
        self.set_interrupted()
        # If waiting for async input, cancel immediately
        if self._waiting_for_input:
            self._waiting_for_input = False
            self.print_str("^C\n")
            self._running = False
            self.print_str("]")

    # -- Initialization --

    def _bind_toolbar(self):
        """Bind toolbar buttons to actions."""
        document["btn-stop"].bind("click", self._on_stop_click)

        def on_run(event):
            editor_content = document["editor"].value
            if hasattr(self, "_repl") and self._repl is not None:
                # Load editor content as program and run
                self._repl._process_line("NEW")
                for raw_line in editor_content.strip().splitlines():
                    raw_line = raw_line.strip()
                    if raw_line:
                        self._repl._process_line(raw_line)
                self._run_program_sliced("RUN")

        document["btn-run"].bind("click", on_run)

        def on_reset(event):
            if hasattr(self, "_repl") and self._repl is not None:
                # If running, stop first
                if self._running:
                    self._running = False
                    self._waiting_for_input = False
                self._repl._process_line("NEW")
                self.clear_screen()
                self.print_str("]")

        document["btn-reset"].bind("click", on_reset)

        def on_list(event):
            if hasattr(self, "_repl") and self._repl is not None:
                self._repl._process_line("LIST")
                self.print_str("]")

        document["btn-list"].bind("click", on_list)


# ---------------------------------------------------------------------------
# Initialization — called when Brython finishes loading
# ---------------------------------------------------------------------------
def init():
    """Initialize the web emulator.

    Creates the IOBridgeWeb, sets up the REPL, and displays the prompt.
    This is the entry point called after Brython initialization.
    """
    io = IOBridgeWeb()

    # Import and create the REPL with our web IOBridge
    try:
        from applesoft.repl import REPL
        from applesoft.debug import DebugTracer

        debug = DebugTracer()
        repl = REPL(io=io, debug=debug)
        io._repl = repl

        # Configure time-slicing: 1000 instructions per slice (~50ms)
        repl.interpreter.set_yield_threshold(1000)
    except Exception as e:
        io.print_str("Error initializing REPL: " + str(e) + "\n")

    # Bind toolbar buttons
    io._bind_toolbar()

    # Hide loading spinner (CA-UC-025-06)
    loading = document["loading-overlay"]
    loading.classList.add("hidden")

    # Show the initial prompt (CA-UC-025-01)
    io.print_str("]")

    # Focus the input field
    io._console_input.focus()


# Run initialization
init()
