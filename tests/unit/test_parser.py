"""Tests unitaires pour le module parser (GRAMMAR.md)."""

from applesoft import ast_nodes as ast
from applesoft.lexer import tokenize
from applesoft.parser import parse_tokens


def parse(line: str) -> ast.StatementList:
    """Helper : tokenise et parse une ligne (sans numéro de ligne)."""
    tokens = tokenize(line)
    from applesoft.lexer import TokenType

    if tokens and tokens[0].type == TokenType.LINENUM:
        tokens = tokens[1:]
    return parse_tokens(tokens)


def print_expr(stmt: ast.PrintStmt, idx: int = 0):
    """Extrait l'expression d'un item PRINT (items sont des tuples (expr, sep))."""
    return stmt.items[idx][0]


class TestPrintStatement:
    """Tests pour l'instruction PRINT."""

    def test_print_string(self):
        result = parse('PRINT "HELLO"')
        stmt = result.statements[0]
        assert isinstance(stmt, ast.PrintStmt)
        expr = print_expr(stmt)
        assert isinstance(expr, ast.StringLiteral)
        assert expr.value == "HELLO"

    def test_print_semicolon(self):
        result = parse('PRINT "A";"B"')
        stmt = result.statements[0]
        assert isinstance(stmt, ast.PrintStmt)
        assert len(stmt.items) == 2

    def test_print_trailing_semicolon(self):
        result = parse('PRINT "A";')
        stmt = result.statements[0]
        assert isinstance(stmt, ast.PrintStmt)
        # Le dernier item a le séparateur ";"
        _, sep = stmt.items[-1]
        assert sep == ";"

    def test_print_empty(self):
        result = parse("PRINT")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.PrintStmt)
        assert len(stmt.items) == 0

    def test_question_mark_is_print(self):
        result = parse('? "HELLO"')
        stmt = result.statements[0]
        assert isinstance(stmt, ast.PrintStmt)


class TestAssignment:
    """Tests pour l'assignation."""

    def test_let_explicit(self):
        result = parse("LET A = 5")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.LetStmt)
        assert isinstance(stmt.target, ast.Variable)
        assert stmt.target.name == "A"

    def test_let_implicit(self):
        result = parse("A = 5")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.LetStmt)


class TestExpressions:
    """Tests pour le parsing des expressions."""

    def test_number_literal(self):
        result = parse("PRINT 42")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.NumberLiteral)
        assert expr.value == 42.0

    def test_binary_op_addition(self):
        result = parse("PRINT 2+3")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.BinaryOp)
        assert expr.op == "+"

    def test_precedence_mul_over_add(self):
        """PRINT 2+3*4 → 2+(3*4)"""
        result = parse("PRINT 2+3*4")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.right, ast.BinaryOp)
        assert expr.right.op == "*"

    def test_parentheses(self):
        """(2+3)*4"""
        result = parse("PRINT (2+3)*4")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.BinaryOp)
        assert expr.op == "*"

    def test_power_right_assoc(self):
        """2^3^2 → 2^(3^2)"""
        result = parse("PRINT 2^3^2")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.BinaryOp)
        assert expr.op == "^"
        assert isinstance(expr.right, ast.BinaryOp)
        assert expr.right.op == "^"

    def test_unary_minus(self):
        result = parse("PRINT -5")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.UnaryOp)
        assert expr.op == "-"

    def test_comparison(self):
        result = parse("PRINT 5>3")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.BinaryOp)
        assert expr.op == ">"

    def test_logical_and_or(self):
        result = parse("PRINT 1 AND 0")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.BinaryOp)
        assert expr.op == "AND"

    def test_not(self):
        result = parse("PRINT NOT 0")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.UnaryOp)
        assert expr.op == "NOT"


class TestControlFlow:
    """Tests pour les structures de contrôle."""

    def test_goto(self):
        result = parse("GOTO 100")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.GotoStmt)
        assert stmt.target == 100

    def test_if_then_number(self):
        """IF X>3 THEN 100 → GOTO implicite"""
        result = parse("IF X>3 THEN 100")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.IfStmt)
        assert isinstance(stmt.then_clause[0], ast.GotoStmt)

    def test_for_next(self):
        result = parse("FOR I=1 TO 10")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.ForStmt)
        assert stmt.var_name == "I"

    def test_for_step(self):
        result = parse("FOR I=1 TO 10 STEP 2")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.ForStmt)
        assert stmt.step is not None

    def test_gosub(self):
        result = parse("GOSUB 1000")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.GosubStmt)
        assert stmt.target == 1000

    def test_return(self):
        result = parse("RETURN")
        assert isinstance(result.statements[0], ast.ReturnStmt)

    def test_on_goto(self):
        result = parse("ON X GOTO 100,200,300")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.OnGotoStmt)
        assert stmt.targets == [100, 200, 300]


class TestCommands:
    """Tests pour les commandes système."""

    def test_list(self):
        result = parse("LIST")
        assert isinstance(result.statements[0], ast.ListStmt)

    def test_list_line(self):
        result = parse("LIST 20")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.ListStmt)
        assert stmt.start == 20
        assert stmt.end == 20

    def test_list_range(self):
        result = parse("LIST 10,20")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.ListStmt)
        assert stmt.start == 10
        assert stmt.end == 20

    def test_new(self):
        result = parse("NEW")
        assert isinstance(result.statements[0], ast.NewStmt)

    def test_del(self):
        result = parse("DEL 10,20")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.DelStmt)
        assert stmt.start == 10
        assert stmt.end == 20

    def test_run(self):
        result = parse("RUN")
        assert isinstance(result.statements[0], ast.RunStmt)

    def test_run_line(self):
        result = parse("RUN 20")
        stmt = result.statements[0]
        assert stmt.start_line == 20


class TestMultiStatement:
    """Tests pour les instructions multi-commandes (RG-0008)."""

    def test_two_statements(self):
        result = parse('PRINT "A" : PRINT "B"')
        assert len(result.statements) == 2

    def test_rem_eats_colon(self):
        """REM absorbe tout, y compris le ':'"""
        result = parse('REM TEXTE : PRINT "CACHÉ"')
        assert len(result.statements) == 1
        assert isinstance(result.statements[0], ast.RemStmt)


class TestFunctions:
    """Tests pour les fonctions intégrées."""

    def test_abs(self):
        result = parse("PRINT ABS(-5)")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.FunctionCall)
        assert expr.name == "ABS"

    def test_left_dollar(self):
        result = parse('PRINT LEFT$("HELLO",3)')
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.FunctionCall)
        assert expr.name == "LEFT$"
        assert len(expr.args) == 2

    def test_peek(self):
        result = parse("PRINT PEEK(49152)")
        stmt = result.statements[0]
        expr = print_expr(stmt)
        assert isinstance(expr, ast.PeekExpr)


class TestDim:
    """Tests pour DIM."""

    def test_dim_single(self):
        result = parse("DIM A(10)")
        stmt = result.statements[0]
        assert isinstance(stmt, ast.DimStmt)
        assert len(stmt.declarations) == 1

    def test_dim_multi(self):
        result = parse("DIM A(5), B(3,4)")
        stmt = result.statements[0]
        assert len(stmt.declarations) == 2
