"""Parser Applesoft BASIC — recursive descent (GRAMMAR.md).

Construit l'AST depuis une liste de tokens.
9 niveaux de précédence des opérateurs.
"""

from __future__ import annotations

from . import ast_nodes as ast
from .errors import BasicSyntaxError
from .lexer import Token, TokenType


class Parser:
    """Parser recursive descent pour Applesoft BASIC."""

    def __init__(self, tokens: list[Token], line_number: int | None = None):
        self.tokens = tokens
        self.pos = 0
        self.line_number = line_number

    def parse(self) -> ast.StatementList:
        """Parse une liste d'instructions (statement_list)."""
        stmts = []
        while not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            # Consommer le séparateur ':' entre instructions
            if self._check(TokenType.COLON):
                self._advance()
            else:
                break
        return ast.StatementList(stmts)

    def _syntax_error(self) -> BasicSyntaxError:
        return BasicSyntaxError(self.line_number)

    def _at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    def _peek(self) -> Token | None:
        if self._at_end():
            return None
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _check(self, token_type: TokenType, value: object = None) -> bool:
        tok = self._peek()
        if tok is None:
            return False
        if tok.type != token_type:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def _expect(self, token_type: TokenType, value: object = None) -> Token:
        if self._check(token_type, value):
            return self._advance()
        raise self._syntax_error()

    def _check_keyword(self, *names: str) -> bool:
        tok = self._peek()
        if tok is None or tok.type != TokenType.KEYWORD:
            return False
        return tok.value in names

    def _expect_keyword(self, name: str) -> Token:
        return self._expect(TokenType.KEYWORD, name)

    # --- Parsing des instructions ---

    def _parse_statement(self) -> object | None:
        """Parse une instruction."""
        tok = self._peek()
        if tok is None:
            return None

        # Commandes système
        if tok.type == TokenType.KEYWORD:
            kw = tok.value
            if kw == "PRINT" or kw == "?":
                return self._parse_print()
            if kw == "INPUT":
                return self._parse_input()
            if kw == "GET":
                return self._parse_get()
            if kw == "LET":
                return self._parse_let()
            if kw == "IF":
                return self._parse_if()
            if kw == "GOTO":
                return self._parse_goto()
            if kw == "GOSUB":
                return self._parse_gosub()
            if kw == "RETURN":
                self._advance()
                return ast.ReturnStmt()
            if kw == "FOR":
                return self._parse_for()
            if kw == "NEXT":
                return self._parse_next()
            if kw == "ON":
                return self._parse_on()
            if kw == "DATA":
                return self._parse_data()
            if kw == "READ":
                return self._parse_read()
            if kw == "RESTORE":
                self._advance()
                return ast.RestoreStmt()
            if kw == "DIM":
                return self._parse_dim()
            if kw == "DEF":
                return self._parse_def_fn()
            if kw == "REM":
                return self._parse_rem()
            if kw == "END":
                self._advance()
                return ast.EndStmt()
            if kw == "STOP":
                self._advance()
                return ast.StopStmt()
            if kw == "POP":
                self._advance()
                return ast.PopStmt()
            if kw == "HOME":
                self._advance()
                return ast.HomeStmt()
            if kw == "HTAB":
                self._advance()
                return ast.HtabStmt(self._parse_expression())
            if kw == "VTAB":
                self._advance()
                return ast.VtabStmt(self._parse_expression())
            if kw == "NORMAL":
                self._advance()
                return ast.NormalStmt()
            if kw == "INVERSE":
                self._advance()
                return ast.InverseStmt()
            if kw == "FLASH":
                self._advance()
                return ast.FlashStmt()
            if kw == "SPEED=" or kw == "SPEED":
                self._advance()
                if kw == "SPEED":
                    self._expect(TokenType.OP, "=")
                return ast.SpeedStmt(self._parse_expression())
            if kw == "TEXT":
                self._advance()
                return ast.TextStmt()
            if kw == "GR":
                self._advance()
                return ast.GrStmt()
            if kw == "COLOR=" or kw == "COLOR":
                self._advance()
                if kw == "COLOR":
                    self._expect(TokenType.OP, "=")
                return ast.ColorStmt(self._parse_expression())
            if kw == "PLOT":
                return self._parse_plot()
            if kw == "HLIN":
                return self._parse_hlin()
            if kw == "VLIN":
                return self._parse_vlin()
            if kw == "HGR":
                self._advance()
                return ast.HgrStmt()
            if kw == "HGR2":
                self._advance()
                return ast.Hgr2Stmt()
            if kw == "HCOLOR=" or kw == "HCOLOR":
                self._advance()
                if kw == "HCOLOR":
                    self._expect(TokenType.OP, "=")
                return ast.HcolorStmt(self._parse_expression())
            if kw == "HPLOT":
                return self._parse_hplot()
            if kw == "DRAW":
                return self._parse_draw()
            if kw == "XDRAW":
                return self._parse_xdraw()
            if kw == "ROT=" or kw == "ROT":
                self._advance()
                if kw == "ROT":
                    self._expect(TokenType.OP, "=")
                return ast.RotStmt(self._parse_expression())
            if kw == "SCALE=" or kw == "SCALE":
                self._advance()
                if kw == "SCALE":
                    self._expect(TokenType.OP, "=")
                return ast.ScaleStmt(self._parse_expression())
            if kw == "POKE":
                return self._parse_poke()
            if kw == "CALL":
                self._advance()
                return ast.CallStmt(self._parse_expression())
            if kw == "ONERR":
                return self._parse_onerr()
            if kw == "RESUME":
                self._advance()
                return ast.ResumeStmt()
            if kw == "CLEAR":
                self._advance()
                return ast.ClearStmt()
            if kw == "SAVE":
                self._advance()
                return ast.SaveStmt(self._parse_expression())
            if kw == "LOAD":
                self._advance()
                return ast.LoadStmt(self._parse_expression())
            if kw == "RUN":
                return self._parse_run()
            if kw == "LIST":
                return self._parse_list()
            if kw == "NEW":
                self._advance()
                return ast.NewStmt()
            if kw == "DEL":
                return self._parse_del()
            if kw == "CONT":
                self._advance()
                return ast.ContStmt()

        # Assignation implicite (sans LET) : identifiant suivi de '='
        if tok.type == TokenType.IDENT:
            return self._parse_assignment()

        raise self._syntax_error()

    def _parse_print(self) -> ast.PrintStmt:
        self._advance()  # Consommer PRINT
        items = []  # list[tuple[expr, sep]]

        while (
            not self._at_end()
            and not self._check(TokenType.COLON)
            and not self._check_keyword("ELSE")
        ):
            # SPC( et TAB(
            if self._check_keyword("SPC("):
                self._advance()
                expr = self._parse_expression()
                self._expect(TokenType.RPAREN)
                item = ast.SpcCall(expr)
            elif self._check_keyword("TAB("):
                self._advance()
                expr = self._parse_expression()
                self._expect(TokenType.RPAREN)
                item = ast.TabCall(expr)
            elif self._check(TokenType.SEMICOLON) or self._check(TokenType.COMMA):
                # Séparateur sans expression avant
                sep = self._advance()
                sep_str = ";" if sep.type == TokenType.SEMICOLON else ","
                # Mettre à jour le séparateur du dernier item
                if items:
                    prev_item, _ = items[-1]
                    items[-1] = (prev_item, sep_str)
                else:
                    # Séparateur en tête — ajouter un item vide
                    items.append((None, sep_str))
                continue
            else:
                item = self._parse_expression()

            # Séparateur après l'expression
            sep = None
            if self._check(TokenType.SEMICOLON):
                self._advance()
                sep = ";"
            elif self._check(TokenType.COMMA):
                self._advance()
                sep = ","

            items.append((item, sep))

        return ast.PrintStmt(items)

    def _parse_input(self) -> ast.InputStmt:
        self._advance()  # Consommer INPUT
        prompt = None

        # Prompt optionnel : "texte";
        if self._check(TokenType.STRING):
            prompt = self._advance().value
            self._expect(TokenType.SEMICOLON)

        variables = [self._parse_variable_ref()]
        while self._check(TokenType.COMMA):
            self._advance()
            variables.append(self._parse_variable_ref())
        return ast.InputStmt(prompt, variables)

    def _parse_get(self) -> ast.GetStmt:
        self._advance()  # Consommer GET
        return ast.GetStmt(self._parse_variable_ref())

    def _parse_let(self) -> ast.LetStmt:
        self._advance()  # Consommer LET
        return self._parse_assignment()

    def _parse_assignment(self) -> ast.LetStmt:
        target = self._parse_variable_ref()
        self._expect(TokenType.OP, "=")
        value = self._parse_expression()
        return ast.LetStmt(target, value)

    def _parse_if(self) -> ast.IfStmt:
        self._advance()  # Consommer IF
        condition = self._parse_expression()
        self._expect_keyword("THEN")

        # THEN suivi d'un numéro = GOTO implicite
        if self._check(TokenType.NUMBER):
            target = int(self._advance().value)
            then_clause = [ast.GotoStmt(target)]
        else:
            then_clause = self._parse_statement_list_until("ELSE")

        # ELSE optionnel
        else_clause = None
        if self._check_keyword("ELSE"):
            self._advance()
            if self._check(TokenType.NUMBER):
                target = int(self._advance().value)
                else_clause = [ast.GotoStmt(target)]
            else:
                else_clause = self._parse_remaining_statements()

        return ast.IfStmt(condition, then_clause, else_clause)

    def _parse_statement_list_until(self, *stop_keywords: str) -> list:
        """Parse des instructions jusqu'à un mot-clé d'arrêt ou fin de ligne."""
        stmts = []
        while not self._at_end():
            if self._check(TokenType.KEYWORD) and self._peek().value in stop_keywords:
                break
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            if self._check(TokenType.COLON):
                self._advance()
            else:
                break
        return stmts

    def _parse_remaining_statements(self) -> list:
        """Parse toutes les instructions restantes."""
        stmts = []
        while not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            if self._check(TokenType.COLON):
                self._advance()
            else:
                break
        return stmts

    def _parse_goto(self) -> ast.GotoStmt:
        self._advance()  # Consommer GOTO
        target = int(self._expect(TokenType.NUMBER).value)
        return ast.GotoStmt(target)

    def _parse_gosub(self) -> ast.GosubStmt:
        self._advance()  # Consommer GOSUB
        target = int(self._expect(TokenType.NUMBER).value)
        return ast.GosubStmt(target)

    def _parse_for(self) -> ast.ForStmt:
        self._advance()  # Consommer FOR
        var_name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.OP, "=")
        start = self._parse_expression()
        self._expect_keyword("TO")
        end = self._parse_expression()
        step = None
        if self._check_keyword("STEP"):
            self._advance()
            step = self._parse_expression()
        return ast.ForStmt(var_name, start, end, step)

    def _parse_next(self) -> ast.NextStmt:
        self._advance()  # Consommer NEXT
        var_names = []
        if self._check(TokenType.IDENT):
            var_names.append(self._advance().value)
            while self._check(TokenType.COMMA):
                self._advance()
                var_names.append(self._expect(TokenType.IDENT).value)
        return ast.NextStmt(var_names)

    def _parse_on(self) -> ast.OnGotoStmt | ast.OnGosubStmt:
        self._advance()  # Consommer ON
        expr = self._parse_expression()
        if self._check_keyword("GOTO"):
            self._advance()
            targets = self._parse_linenum_list()
            return ast.OnGotoStmt(expr, targets)
        elif self._check_keyword("GOSUB"):
            self._advance()
            targets = self._parse_linenum_list()
            return ast.OnGosubStmt(expr, targets)
        raise self._syntax_error()

    def _parse_linenum_list(self) -> list[int]:
        targets = [int(self._expect(TokenType.NUMBER).value)]
        while self._check(TokenType.COMMA):
            self._advance()
            targets.append(int(self._expect(TokenType.NUMBER).value))
        return targets

    def _parse_data(self) -> ast.DataStmt:
        self._advance()  # Consommer DATA
        # DATA est spécial : les valeurs sont lues comme du texte brut
        values = []
        current = ""
        while not self._at_end() and not self._check(TokenType.COLON):
            tok = self._advance()
            if tok.type == TokenType.COMMA:
                values.append(current.strip())
                current = ""
            elif tok.type == TokenType.STRING:
                current = tok.value
            else:
                if current:
                    current += " "
                current += str(tok.value) if tok.value is not None else ""
        values.append(current.strip())
        return ast.DataStmt(values)

    def _parse_read(self) -> ast.ReadStmt:
        self._advance()  # Consommer READ
        variables = [self._parse_variable_ref()]
        while self._check(TokenType.COMMA):
            self._advance()
            variables.append(self._parse_variable_ref())
        return ast.ReadStmt(variables)

    def _parse_dim(self) -> ast.DimStmt:
        self._advance()  # Consommer DIM
        declarations = [self._parse_dim_decl()]
        while self._check(TokenType.COMMA):
            self._advance()
            declarations.append(self._parse_dim_decl())
        return ast.DimStmt(declarations)

    def _parse_dim_decl(self) -> tuple[str, list]:
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.LPAREN)
        dims = [self._parse_expression()]
        while self._check(TokenType.COMMA):
            self._advance()
            dims.append(self._parse_expression())
        self._expect(TokenType.RPAREN)
        return (name, dims)

    def _parse_def_fn(self) -> ast.DefFnStmt:
        self._advance()  # Consommer DEF
        self._expect_keyword("FN")
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.LPAREN)
        param = self._expect(TokenType.IDENT).value
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.OP, "=")
        body = self._parse_expression()
        return ast.DefFnStmt(name, param, body)

    def _parse_rem(self) -> ast.RemStmt:
        self._advance()  # Consommer REM
        # Le token suivant (si présent) est le texte du commentaire (STRING)
        text = ""
        if not self._at_end() and self._peek().type == TokenType.STRING:
            text = self._advance().value
        # Consommer tous les tokens restants (REM mange tout)
        while not self._at_end():
            self._advance()
        return ast.RemStmt(text)

    def _parse_run(self) -> ast.RunStmt:
        self._advance()  # Consommer RUN
        start_line = None
        if self._check(TokenType.NUMBER):
            start_line = int(self._advance().value)
        return ast.RunStmt(start_line)

    def _parse_list(self) -> ast.ListStmt:
        self._advance()  # Consommer LIST
        start = None
        end = None
        if self._check(TokenType.NUMBER):
            start = int(self._advance().value)
            if self._check(TokenType.COMMA):
                self._advance()
                if self._check(TokenType.NUMBER):
                    end = int(self._advance().value)
            else:
                end = start  # LIST 20 = afficher uniquement la ligne 20
        return ast.ListStmt(start, end)

    def _parse_del(self) -> ast.DelStmt:
        self._advance()  # Consommer DEL
        start = int(self._expect(TokenType.NUMBER).value)
        self._expect(TokenType.COMMA)
        end = int(self._expect(TokenType.NUMBER).value)
        return ast.DelStmt(start, end)

    def _parse_plot(self) -> ast.PlotStmt:
        self._advance()  # Consommer PLOT
        x = self._parse_expression()
        self._expect(TokenType.COMMA)
        y = self._parse_expression()
        return ast.PlotStmt(x, y)

    def _parse_hlin(self) -> ast.HlinStmt:
        self._advance()  # Consommer HLIN
        x1 = self._parse_expression()
        self._expect(TokenType.COMMA)
        x2 = self._parse_expression()
        self._expect_keyword("AT")
        y = self._parse_expression()
        return ast.HlinStmt(x1, x2, y)

    def _parse_vlin(self) -> ast.VlinStmt:
        self._advance()  # Consommer VLIN
        y1 = self._parse_expression()
        self._expect(TokenType.COMMA)
        y2 = self._parse_expression()
        self._expect_keyword("AT")
        x = self._parse_expression()
        return ast.VlinStmt(y1, y2, x)

    def _parse_hplot(self) -> ast.HplotStmt:
        self._advance()  # Consommer HPLOT
        from_last = False
        points = []

        if self._check_keyword("TO"):
            from_last = True
        else:
            x = self._parse_expression()
            self._expect(TokenType.COMMA)
            y = self._parse_expression()
            points.append((x, y))

        while self._check_keyword("TO"):
            self._advance()
            x = self._parse_expression()
            self._expect(TokenType.COMMA)
            y = self._parse_expression()
            points.append((x, y))

        return ast.HplotStmt(points, from_last)

    def _parse_draw(self) -> ast.DrawStmt:
        self._advance()  # Consommer DRAW
        shape = self._parse_expression()
        self._expect_keyword("AT")
        x = self._parse_expression()
        self._expect(TokenType.COMMA)
        y = self._parse_expression()
        return ast.DrawStmt(shape, x, y)

    def _parse_xdraw(self) -> ast.XdrawStmt:
        self._advance()  # Consommer XDRAW
        shape = self._parse_expression()
        self._expect_keyword("AT")
        x = self._parse_expression()
        self._expect(TokenType.COMMA)
        y = self._parse_expression()
        return ast.XdrawStmt(shape, x, y)

    def _parse_poke(self) -> ast.PokeStmt:
        self._advance()  # Consommer POKE
        address = self._parse_expression()
        self._expect(TokenType.COMMA)
        value = self._parse_expression()
        return ast.PokeStmt(address, value)

    def _parse_onerr(self) -> ast.OnerrStmt:
        self._advance()  # Consommer ONERR
        self._expect_keyword("GOTO")
        target = int(self._expect(TokenType.NUMBER).value)
        return ast.OnerrStmt(target)

    def _parse_variable_ref(self) -> ast.Variable | ast.ArrayAccess:
        """Parse une référence à une variable ou un accès tableau."""
        name = self._expect(TokenType.IDENT).value
        if self._check(TokenType.LPAREN):
            self._advance()
            indices = [self._parse_expression()]
            while self._check(TokenType.COMMA):
                self._advance()
                indices.append(self._parse_expression())
            self._expect(TokenType.RPAREN)
            return ast.ArrayAccess(name, indices)
        return ast.Variable(name)

    # --- Parsing des expressions (9 niveaux de précédence) ---

    def _parse_expression(self) -> object:
        """Parse une expression (niveau le plus bas : OR)."""
        return self._parse_or()

    def _parse_or(self) -> object:
        left = self._parse_and()
        while self._check_keyword("OR"):
            self._advance()
            right = self._parse_and()
            left = ast.BinaryOp("OR", left, right)
        return left

    def _parse_and(self) -> object:
        left = self._parse_not()
        while self._check_keyword("AND"):
            self._advance()
            right = self._parse_not()
            left = ast.BinaryOp("AND", left, right)
        return left

    def _parse_not(self) -> object:
        if self._check_keyword("NOT"):
            self._advance()
            operand = self._parse_not()
            return ast.UnaryOp("NOT", operand)
        return self._parse_comparison()

    def _parse_comparison(self) -> object:
        left = self._parse_addition()
        while self._check(TokenType.OP) and self._peek().value in (
            "=",
            "<>",
            "><",
            "<",
            ">",
            "<=",
            "=<",
            ">=",
            "=>",
        ):
            op = self._advance().value
            right = self._parse_addition()
            left = ast.BinaryOp(op, left, right)
        return left

    def _parse_addition(self) -> object:
        left = self._parse_multiplication()
        while self._check(TokenType.OP) and self._peek().value in ("+", "-"):
            op = self._advance().value
            right = self._parse_multiplication()
            left = ast.BinaryOp(op, left, right)
        return left

    def _parse_multiplication(self) -> object:
        left = self._parse_power()
        while self._check(TokenType.OP) and self._peek().value in ("*", "/"):
            op = self._advance().value
            right = self._parse_power()
            left = ast.BinaryOp(op, left, right)
        return left

    def _parse_power(self) -> object:
        base = self._parse_unary()
        if self._check(TokenType.OP, "^"):
            self._advance()
            # Associativité droite : récursion
            exponent = self._parse_power()
            return ast.BinaryOp("^", base, exponent)
        return base

    def _parse_unary(self) -> object:
        if self._check(TokenType.OP, "-"):
            self._advance()
            operand = self._parse_unary()
            return ast.UnaryOp("-", operand)
        if self._check(TokenType.OP, "+"):
            self._advance()
            return self._parse_unary()
        return self._parse_primary()

    def _parse_primary(self) -> object:
        tok = self._peek()
        if tok is None:
            raise self._syntax_error()

        # Nombre
        if tok.type == TokenType.NUMBER:
            self._advance()
            return ast.NumberLiteral(tok.value)

        # Chaîne
        if tok.type == TokenType.STRING:
            self._advance()
            return ast.StringLiteral(tok.value)

        # Parenthèse
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return ast.ParenExpr(expr)

        # Fonctions intégrées
        if tok.type == TokenType.KEYWORD:
            kw = tok.value
            # Fonctions avec parenthèse incluse dans le token
            if kw == "SCRN(":
                self._advance()
                x = self._parse_expression()
                self._expect(TokenType.COMMA)
                y = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return ast.ScrnExpr(x, y)
            if kw == "SPC(":
                self._advance()
                expr = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return ast.SpcCall(expr)
            if kw == "TAB(":
                self._advance()
                expr = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return ast.TabCall(expr)

            # Fonctions standard func(expr)
            if kw in _BUILTIN_FUNCTIONS:
                self._advance()
                self._expect(TokenType.LPAREN)
                args = [self._parse_expression()]
                # Fonctions multi-arguments
                if kw in ("LEFT$", "RIGHT$", "MID$"):
                    self._expect(TokenType.COMMA)
                    args.append(self._parse_expression())
                    if kw == "MID$" and self._check(TokenType.COMMA):
                        self._advance()
                        args.append(self._parse_expression())
                self._expect(TokenType.RPAREN)
                return ast.FunctionCall(kw, args)

            # PEEK
            if kw == "PEEK":
                self._advance()
                self._expect(TokenType.LPAREN)
                addr = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return ast.PeekExpr(addr)

            # POS
            if kw == "POS":
                self._advance()
                self._expect(TokenType.LPAREN)
                arg = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return ast.PosExpr(arg)

            # FN call
            if kw == "FN":
                self._advance()
                name = self._expect(TokenType.IDENT).value
                self._expect(TokenType.LPAREN)
                arg = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return ast.FnCall(name, arg)

        # Variable ou accès tableau
        if tok.type == TokenType.IDENT:
            return self._parse_variable_or_array()

        raise self._syntax_error()

    def _parse_variable_or_array(self) -> ast.Variable | ast.ArrayAccess:
        name = self._advance().value
        if self._check(TokenType.LPAREN):
            self._advance()
            indices = [self._parse_expression()]
            while self._check(TokenType.COMMA):
                self._advance()
                indices.append(self._parse_expression())
            self._expect(TokenType.RPAREN)
            return ast.ArrayAccess(name, indices)
        return ast.Variable(name)


# Fonctions intégrées qui prennent des parenthèses
_BUILTIN_FUNCTIONS = {
    "ABS",
    "INT",
    "SGN",
    "SQR",
    "LOG",
    "EXP",
    "SIN",
    "COS",
    "TAN",
    "ATN",
    "RND",
    "LEN",
    "LEFT$",
    "RIGHT$",
    "MID$",
    "ASC",
    "CHR$",
    "STR$",
    "VAL",
}


def parse_tokens(tokens: list[Token], line_number: int | None = None) -> ast.StatementList:
    """Parse une liste de tokens en AST."""
    parser = Parser(tokens, line_number)
    return parser.parse()
