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
# Applesoft BASIC keywords for syntax highlighting (CA-UC-026-01)
# ---------------------------------------------------------------------------
APPLESOFT_KEYWORDS = {
    "ABS", "AND", "ASC", "AT", "ATN", "CALL", "CHR$", "CLEAR", "COLOR",
    "CONT", "COS", "DATA", "DEF", "DEL", "DIM", "DRAW", "END", "EXP",
    "FLASH", "FN", "FOR", "FRE", "GET", "GOSUB", "GOTO", "GR", "HCOLOR",
    "HGR", "HGR2", "HIMEM:", "HLIN", "HOME", "HPLOT", "HTAB", "IF",
    "IN#", "INPUT", "INT", "INVERSE", "LEFT$", "LEN", "LET", "LIST",
    "LOAD", "LOG", "LOMEM:", "MID$", "NEW", "NEXT", "NORMAL", "NOT",
    "NOTRACE", "ON", "ONERR", "OR", "PDL", "PEEK", "PLOT", "POKE",
    "POP", "POS", "PRINT", "READ", "RECALL", "REM", "RESTORE", "RESUME",
    "RETURN", "RIGHT$", "RND", "ROT", "RUN", "SAVE", "SCALE", "SCRN",
    "SGN", "SIN", "SPC", "SPEED", "SQR", "STEP", "STOP", "STORE",
    "STR$", "TAB", "TAN", "TEXT", "THEN", "TO", "TRACE", "USR", "VAL",
    "VLIN", "VTAB", "WAIT", "XDRAW", "ELSE",
}


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

        self._editor = document["editor"]
        self._editor_highlight = document["editor-highlight"]

        # Bind keyboard events for GET support and interrupt
        self._console_input.bind("keydown", self._on_keydown)
        # Capture Ctrl+C on the whole document (not just the input field)
        document.bind("keydown", self._on_document_keydown)

        # Bind editor events for syntax highlighting (CA-UC-026-01)
        self._editor.bind("input", self._on_editor_input)
        self._editor.bind("scroll", self._on_editor_scroll)

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

    # -- Syntax highlighting (CA-UC-026-01) --

    def _on_editor_input(self, event):
        """Re-highlight the editor content on every input change."""
        self._highlight_editor()

    def _on_editor_scroll(self, event):
        """Sync the highlight overlay scroll position with the textarea."""
        self._editor_highlight.scrollTop = self._editor.scrollTop
        self._editor_highlight.scrollLeft = self._editor.scrollLeft

    def _highlight_editor(self):
        """Apply syntax highlighting to the editor content.

        Tokenizes the text and renders colored spans into the overlay div.
        Uses textContent exclusively (SEC-DEV-03, SEC-BP-24).
        """
        text = self._editor.value

        # Clear overlay via DOM removal (SEC-DEV-03)
        while self._editor_highlight.firstChild:
            self._editor_highlight.removeChild(self._editor_highlight.firstChild)

        if not text:
            return

        for line in text.split("\n"):
            self._highlight_line(line)
            # Add newline between lines
            br = document.createElement("br")
            self._editor_highlight.appendChild(br)

    def _highlight_line(self, line):
        """Highlight a single line of Applesoft BASIC code.

        Scans for: line numbers, keywords, strings, REM comments.
        Creates <span> elements with appropriate CSS classes.
        """
        upper = line.upper()
        i = 0
        n = len(line)

        # Skip leading spaces
        while i < n and line[i] == " ":
            i += 1
        if i > 0:
            self._append_span(line[:i], "")

        # Line number
        num_start = i
        while i < n and line[i].isdigit():
            i += 1
        if i > num_start:
            self._append_span(line[num_start:i], "number-literal")

        # Skip space after line number
        if i < n and line[i] == " ":
            self._append_span(" ", "")
            i += 1

        # Check for REM — rest of line is a comment
        if upper[i:].startswith("REM"):
            self._append_span(line[i:], "remark")
            return

        # Scan tokens
        while i < n:
            ch = line[i]

            # String literal
            if ch == '"':
                j = i + 1
                while j < n and line[j] != '"':
                    j += 1
                if j < n:
                    j += 1  # include closing quote
                self._append_span(line[i:j], "string-literal")
                i = j
                continue

            # Try to match a keyword
            matched = self._match_keyword(upper, i)
            if matched:
                self._append_span(line[i:i + len(matched)], "keyword")
                i += len(matched)
                # REM keyword — rest of line is comment
                if matched == "REM":
                    if i < n:
                        self._append_span(line[i:], "remark")
                    return
                continue

            # Regular character
            self._append_span(ch, "")
            i += 1

    def _match_keyword(self, upper_line, pos):
        """Try to match an Applesoft keyword at position pos (longest match)."""
        best = ""
        for kw in APPLESOFT_KEYWORDS:
            if upper_line[pos:pos + len(kw)] == kw and len(kw) > len(best):
                best = kw
        return best

    def _append_span(self, text, css_class):
        """Append a <span> with textContent to the highlight overlay.

        Uses textContent exclusively (SEC-DEV-03).
        """
        span = document.createElement("span")
        span.textContent = text
        if css_class:
            span.className = css_class
        self._editor_highlight.appendChild(span)

    # -- Editor ↔ Console synchronization (CA-UC-026-04) --

    def _update_editor(self):
        """Synchronize the editor textarea with the current program in memory.

        Called after a console command modifies the program (e.g., entering
        a numbered line or DEL).
        """
        if not hasattr(self, "_repl") or self._repl is None:
            return
        prog = self._repl.interpreter.program
        lines = prog.list_lines()
        text_lines = []
        for line_num in lines:
            tokens = prog.get_line(line_num)
            if tokens is not None:
                text = str(line_num) + " " + " ".join(
                    t.value for t in tokens
                )
                text_lines.append(text)
        self._editor.value = "\n".join(text_lines)
        self._highlight_editor()

    # -- Column mode switching (CA-UC-025-07, CA-UC-025-08) --

    def set_column_mode(self, columns):
        """Switch between 40 and 80 column display modes."""
        if columns == 80:
            self._console_output.classList.add("mode-80")
        else:
            self._console_output.classList.remove("mode-80")

    # -- Persistence: localStorage + file I/O (CA-UC-028-01 to CA-UC-028-06) --

    # Maximum import file size: 1 Mo (SEC-BP-41)
    MAX_IMPORT_SIZE = 1_000_000

    # Accepted file extensions for import (SEC-BP-40)
    ALLOWED_EXTENSIONS = (".bas", ".txt")

    def save_to_localStorage(self, name, program_text):
        """Save a program to localStorage (CA-UC-028-01).

        Stores under key 'applesoft:<name>' with metadata.
        Raises BasicError-like message if localStorage is full or disabled.
        """
        key = "applesoft:" + name
        try:
            storage = window.localStorage
            import json
            data = json.dumps({
                "name": name,
                "code": program_text,
                "date": str(window.Date.new().toISOString()),
            })
            storage.setItem(key, data)
        except Exception:
            self.print_str("?OUT OF MEMORY ERROR\n")

    def load_from_localStorage(self, name):
        """Load a program from localStorage (CA-UC-028-02).

        Returns the program text, or None if not found.
        """
        key = "applesoft:" + name
        try:
            storage = window.localStorage
            raw = storage.getItem(key)
            if raw is None:
                return None
            import json
            data = json.loads(raw)
            return data.get("code", "")
        except Exception:
            self.print_str("?STORAGE ERROR\n")
            return None

    def list_saved_programs(self):
        """List all saved programs in localStorage (CA-UC-028-03).

        Returns a list of (name, date) tuples.
        """
        programs = []
        try:
            storage = window.localStorage
            import json
            for i in range(storage.length):
                key = storage.key(i)
                if key.startswith("applesoft:"):
                    name = key[len("applesoft:"):]
                    raw = storage.getItem(key)
                    data = json.loads(raw)
                    programs.append((name, data.get("date", "")))
        except Exception:
            pass
        return programs

    def export_file(self, filename, content):
        """Export a program as a downloadable .bas file (CA-UC-028-05).

        Creates a Blob and triggers a download via a temporary <a> element.
        """
        if not filename.endswith(".bas"):
            filename += ".bas"
        blob = window.Blob.new([content], {"type": "text/plain"})
        url = window.URL.createObjectURL(blob)
        a = document.createElement("a")
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)

    def _validate_import_file(self, file):
        """Validate an imported file (SEC-BP-40, SEC-BP-41).

        Checks file extension and size before reading.
        Returns True if valid, False otherwise.
        """
        name = file.name.lower()
        valid_ext = any(name.endswith(ext) for ext in self.ALLOWED_EXTENSIONS)
        if not valid_ext:
            self.print_str("?FILE TYPE ERROR — only .bas and .txt files accepted\n")
            return False
        if file.size > self.MAX_IMPORT_SIZE:
            self.print_str("?FILE TOO LARGE ERROR — max 1 Mo\n")
            return False
        return True

    def _import_file_content(self, content):
        """Load imported file content into the editor and program memory."""
        self._editor.value = content
        self._highlight_editor()
        if hasattr(self, "_repl") and self._repl is not None:
            self._repl._process_line("NEW")
            for line in content.strip().splitlines():
                line = line.strip()
                if line:
                    self._repl._process_line(line)

    def _setup_file_import(self):
        """Set up file import via hidden <input type=file> (CA-UC-028-04)."""
        file_input = document.createElement("input")
        file_input.type = "file"
        file_input.accept = ".bas,.txt"
        file_input.style.display = "none"
        document.body.appendChild(file_input)
        self._file_input = file_input

        def on_file_selected(event):
            files = file_input.files
            if files.length == 0:
                return
            f = files[0]
            if not self._validate_import_file(f):
                return
            reader = window.FileReader.new()
            reader.onload = lambda e: self._import_file_content(e.target.result)
            reader.readAsText(f)

        file_input.bind("change", on_file_selected)

    def _setup_drag_drop(self):
        """Set up drag & drop .bas import on the editor (CA-UC-028-06)."""
        def on_dragover(event):
            event.preventDefault()
            event.dataTransfer.dropEffect = "copy"

        def on_drop(event):
            event.preventDefault()
            files = event.dataTransfer.files
            if files.length == 0:
                return
            f = files[0]
            if not self._validate_import_file(f):
                return
            reader = window.FileReader.new()
            reader.onload = lambda e: self._import_file_content(e.target.result)
            reader.readAsText(f)

        self._editor.bind("dragover", on_dragover)
        self._editor.bind("drop", on_drop)

    # -- Canvas graphics (CA-UC-027-01 to CA-UC-027-04) --

    # Apple II LoRes 16-color palette (CA-UC-027-02)
    LORES_COLORS = [
        "#000000", "#DD0033", "#000099", "#DD22DD",
        "#007700", "#555555", "#2222FF", "#6699FF",
        "#885500", "#FF6600", "#AAAAAA", "#FF9988",
        "#11DD00", "#FFFF00", "#44FF99", "#FFFFFF",
    ]

    # Apple II HiRes 8-color palette
    HIRES_COLORS = [
        "#000000", "#11DD00", "#FF6600", "#FFFFFF",
        "#000000", "#2222FF", "#FF44DD", "#FFFFFF",
    ]

    def _show_canvas(self, width, height):
        """Show the graphics canvas and set its logical size.

        Called when GR (40x48), HGR (280x192), or HGR2 is executed.
        """
        canvas_section = document["canvas-section"]
        canvas_section.style.display = "flex"
        canvas = document["graphics-canvas"]
        canvas.width = width
        canvas.height = height

    def _hide_canvas(self):
        """Hide the graphics canvas (called on TEXT command)."""
        document["canvas-section"].style.display = "none"

    def render_lores(self, buffer):
        """Render the LoRes 40x48 grid to the canvas.

        Uses fillRect for each cell. Each cell is rendered as a solid
        color rectangle scaled to fill the canvas.
        """
        canvas = document["graphics-canvas"]
        ctx = canvas.getContext("2d")
        cell_w = canvas.width / 40
        cell_h = canvas.height / 48
        for y in range(48):
            for x in range(40):
                color_idx = buffer[y][x] if y < len(buffer) and x < len(buffer[y]) else 0
                ctx.fillStyle = self.LORES_COLORS[color_idx % 16]
                ctx.fillRect(x * cell_w, y * cell_h, cell_w, cell_h)

    def render_hires(self, buffer, width=280, height=192):
        """Render the HiRes 280x192 buffer to the canvas.

        Each pixel is drawn individually. Canvas uses integer upscale
        without anti-aliasing (CSS image-rendering: pixelated).
        """
        canvas = document["graphics-canvas"]
        ctx = canvas.getContext("2d")
        for y in range(min(height, len(buffer))):
            for x in range(min(width, len(buffer[y]))):
                color_idx = buffer[y][x]
                ctx.fillStyle = self.HIRES_COLORS[color_idx % 8]
                ctx.fillRect(x, y, 1, 1)

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

        # Sync editor if the command may have modified the program (CA-UC-026-04)
        stripped = line.strip()
        if stripped and (stripped[0].isdigit() or upper.startswith("NEW") or upper.startswith("DEL")):
            self._update_editor()

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
                # If already running, interrupt first (CA-UC-025 exception)
                if self._running:
                    self._running = False
                    self._waiting_for_input = False
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
                self._editor.value = ""
                self._highlight_editor()
                self.print_str("]")

        document["btn-reset"].bind("click", on_reset)

        def on_list(event):
            if hasattr(self, "_repl") and self._repl is not None:
                self._repl._process_line("LIST")
                self.print_str("]")

        document["btn-list"].bind("click", on_list)

        # SAVE button — export current program as .bas file (CA-UC-028-05)
        def on_save(event):
            if hasattr(self, "_repl") and self._repl is not None:
                content = self._editor.value
                self.export_file("program", content)

        document["btn-save"].bind("click", on_save)

        # LOAD button — import .bas file via file picker (CA-UC-028-04)
        self._setup_file_import()

        def on_load(event):
            self._file_input.click()

        document["btn-load"].bind("click", on_load)

        # Drag & drop on editor (CA-UC-028-06)
        self._setup_drag_drop()


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
