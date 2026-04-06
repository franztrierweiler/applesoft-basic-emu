"""Nœuds AST pour Applesoft BASIC.

Chaque construction du langage est représentée par un nœud typé.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- Expressions ---


@dataclass
class NumberLiteral:
    value: float


@dataclass
class StringLiteral:
    value: str


@dataclass
class Variable:
    name: str  # Nom normalisé (2 chars + suffixe)


@dataclass
class ArrayAccess:
    name: str
    indices: list  # list[Expression]


@dataclass
class BinaryOp:
    op: str
    left: object  # Expression
    right: object  # Expression


@dataclass
class UnaryOp:
    op: str
    operand: object  # Expression


@dataclass
class FunctionCall:
    name: str
    args: list  # list[Expression]


@dataclass
class FnCall:
    name: str  # Nom de la fonction FN (ex: "DOUBLE")
    arg: object  # Expression


@dataclass
class PeekExpr:
    address: object  # Expression


@dataclass
class ScrnExpr:
    x: object  # Expression
    y: object  # Expression


@dataclass
class PosExpr:
    arg: object  # Expression (évalué mais ignoré)


@dataclass
class SpcCall:
    count: object  # Expression


@dataclass
class TabCall:
    column: object  # Expression


@dataclass
class ParenExpr:
    expr: object  # Expression


# --- Instructions ---


@dataclass
class PrintStmt:
    items: list  # list[tuple[Expression | SpcCall | TabCall, str | None]]
    # Chaque item est (expression, séparateur suivant: ';', ',', ou None)


@dataclass
class InputStmt:
    prompt: str | None
    variables: list  # list[Variable | ArrayAccess]


@dataclass
class GetStmt:
    variable: object  # Variable


@dataclass
class LetStmt:
    target: object  # Variable ou ArrayAccess
    value: object  # Expression


@dataclass
class IfStmt:
    condition: object  # Expression
    then_clause: list  # list[Statement]
    else_clause: list | None = None  # list[Statement] | None


@dataclass
class GotoStmt:
    target: int


@dataclass
class GosubStmt:
    target: int


@dataclass
class ReturnStmt:
    pass


@dataclass
class ForStmt:
    var_name: str
    start: object  # Expression
    end: object  # Expression
    step: object | None = None  # Expression | None


@dataclass
class NextStmt:
    var_names: list[str]  # Peut être vide (NEXT sans variable)


@dataclass
class OnGotoStmt:
    expr: object  # Expression
    targets: list[int]


@dataclass
class OnGosubStmt:
    expr: object  # Expression
    targets: list[int]


@dataclass
class DataStmt:
    values: list[str]


@dataclass
class ReadStmt:
    variables: list  # list[Variable | ArrayAccess]


@dataclass
class RestoreStmt:
    pass


@dataclass
class DimStmt:
    declarations: list[tuple[str, list]]  # [(nom, [dimensions])]


@dataclass
class DefFnStmt:
    name: str  # Nom de la fonction (ex: "DOUBLE")
    param: str  # Nom du paramètre
    body: object  # Expression


@dataclass
class RemStmt:
    text: str = ""


@dataclass
class EndStmt:
    pass


@dataclass
class StopStmt:
    pass


@dataclass
class PopStmt:
    pass


@dataclass
class HomeStmt:
    pass


@dataclass
class HtabStmt:
    column: object  # Expression


@dataclass
class VtabStmt:
    row: object  # Expression


@dataclass
class NormalStmt:
    pass


@dataclass
class InverseStmt:
    pass


@dataclass
class FlashStmt:
    pass


@dataclass
class SpeedStmt:
    value: object  # Expression


@dataclass
class TextStmt:
    pass


@dataclass
class GrStmt:
    pass


@dataclass
class ColorStmt:
    value: object  # Expression


@dataclass
class PlotStmt:
    x: object  # Expression
    y: object  # Expression


@dataclass
class HlinStmt:
    x1: object
    x2: object
    y: object


@dataclass
class VlinStmt:
    y1: object
    y2: object
    x: object


@dataclass
class HgrStmt:
    pass


@dataclass
class Hgr2Stmt:
    pass


@dataclass
class HcolorStmt:
    value: object  # Expression


@dataclass
class HplotStmt:
    points: list[tuple]  # list[(Expression, Expression)]
    from_last: bool = False  # HPLOT TO (depuis dernière position)


@dataclass
class DrawStmt:
    shape: object  # Expression
    x: object
    y: object


@dataclass
class XdrawStmt:
    shape: object  # Expression
    x: object
    y: object


@dataclass
class RotStmt:
    value: object  # Expression


@dataclass
class ScaleStmt:
    value: object  # Expression


@dataclass
class PokeStmt:
    address: object  # Expression
    value: object  # Expression


@dataclass
class CallStmt:
    address: object  # Expression


@dataclass
class OnerrStmt:
    target: int


@dataclass
class ResumeStmt:
    pass


@dataclass
class ClearStmt:
    pass


@dataclass
class SaveStmt:
    filename: object  # Expression (string)


@dataclass
class LoadStmt:
    filename: object  # Expression (string)


@dataclass
class RunStmt:
    start_line: int | None = None


@dataclass
class ListStmt:
    start: int | None = None
    end: int | None = None


@dataclass
class NewStmt:
    pass


@dataclass
class DelStmt:
    start: int
    end: int


@dataclass
class ContStmt:
    pass


@dataclass
class StatementList:
    """Liste d'instructions sur une même ligne."""

    statements: list = field(default_factory=list)
