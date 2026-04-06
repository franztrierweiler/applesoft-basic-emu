"""État d'exécution Applesoft BASIC.

Gère les variables, tableaux, piles GOSUB/FOR, pointeur DATA,
définitions FN, état CONT, état d'affichage.
"""

from __future__ import annotations

from .errors import BasicError


class Environment:
    """État d'exécution de l'interpréteur."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Réinitialise tout l'état (appelé par RUN)."""
        self._variables: dict[str, float | int | str] = {}
        self._arrays: dict[str, tuple[list[int], list]] = {}
        self._gosub_stack: list[tuple[int, int]] = []  # (line_num, stmt_idx)
        self._for_stack: list[dict] = []
        self._data_pointer: int = 0
        self._data_values: list[str] = []
        self._fn_defs: dict[str, tuple[str, object]] = {}
        self._cont_point: tuple[int, int] | None = None
        self._program_modified: bool = False
        self._stopped: bool = False

    # --- Variables ---

    def get_var(self, name: str) -> float | int | str:
        """Retourne la valeur d'une variable (0 ou "" si non initialisée)."""
        if name in self._variables:
            return self._variables[name]
        # Valeur par défaut selon le type
        if name.endswith("$"):
            return ""
        return 0

    def set_var(self, name: str, value: float | int | str) -> None:
        """Assigne une valeur à une variable avec vérification de type."""
        _check_type_assignment(name, value)
        if name.endswith("%"):
            value = _to_integer(value)
        self._variables[name] = value

    # --- Tableaux ---

    def dim_array(self, name: str, dimensions: list[int]) -> None:
        """Déclare un tableau avec DIM."""
        if name in self._arrays:
            raise BasicError(120)  # REDIM'D ARRAY
        for d in dimensions:
            if d < 0:
                raise BasicError(53)  # ILLEGAL QUANTITY
        # Les indices vont de 0 à dim inclus → dim+1 éléments
        sizes = [d + 1 for d in dimensions]
        total = 1
        for s in sizes:
            total *= s
        default = "" if name.endswith("$") else 0
        data = [default] * total
        self._arrays[name] = (sizes, data)

    def get_array(self, name: str, indices: list[int]) -> float | int | str:
        """Lit une valeur dans un tableau."""
        self._ensure_array(name, indices)
        sizes, data = self._arrays[name]
        idx = self._flat_index(sizes, indices)
        return data[idx]

    def set_array(self, name: str, indices: list[int], value: float | int | str) -> None:
        """Écrit une valeur dans un tableau."""
        _check_type_assignment(name, value)
        if name.endswith("%"):
            value = _to_integer(value)
        self._ensure_array(name, indices)
        sizes, data = self._arrays[name]
        idx = self._flat_index(sizes, indices)
        data[idx] = value

    def _ensure_array(self, name: str, indices: list[int]) -> None:
        """Auto-dimensionne un tableau à 10 si non déclaré."""
        if name not in self._arrays:
            dims = [10] * len(indices)
            self.dim_array(name, dims)
        sizes, _ = self._arrays[name]
        if len(indices) != len(sizes):
            raise BasicError(107)  # BAD SUBSCRIPT
        for i, idx in enumerate(indices):
            if idx < 0 or idx >= sizes[i]:
                raise BasicError(107)  # BAD SUBSCRIPT

    def _flat_index(self, sizes: list[int], indices: list[int]) -> int:
        """Calcule l'index plat pour un tableau multidimensionnel."""
        idx = 0
        multiplier = 1
        for i in range(len(sizes) - 1, -1, -1):
            idx += indices[i] * multiplier
            multiplier *= sizes[i]
        return idx

    # --- Piles GOSUB / FOR ---

    def push_gosub(self, line_num: int, stmt_idx: int) -> None:
        self._gosub_stack.append((line_num, stmt_idx))

    def pop_gosub(self) -> tuple[int, int]:
        if not self._gosub_stack:
            raise BasicError(22)  # RETURN WITHOUT GOSUB
        return self._gosub_stack.pop()

    def push_for(self, info: dict) -> None:
        # Supprimer une boucle FOR existante sur la même variable
        self._for_stack = [f for f in self._for_stack if f["var"] != info["var"]]
        self._for_stack.append(info)

    def pop_for(self, var_name: str | None = None) -> dict:
        if not self._for_stack:
            raise BasicError(0)  # NEXT WITHOUT FOR
        if var_name is None:
            return self._for_stack.pop()
        # Chercher la boucle correspondante, en dépilant les boucles internes
        while self._for_stack:
            top = self._for_stack[-1]
            if top["var"] == var_name:
                return self._for_stack.pop()
            self._for_stack.pop()
        raise BasicError(0)  # NEXT WITHOUT FOR

    def peek_for(self, var_name: str | None = None) -> dict:
        """Consulte la boucle FOR sans la dépiler."""
        if not self._for_stack:
            raise BasicError(0)
        if var_name is None:
            return self._for_stack[-1]
        for i in range(len(self._for_stack) - 1, -1, -1):
            if self._for_stack[i]["var"] == var_name:
                return self._for_stack[i]
        raise BasicError(0)

    # --- DATA ---

    def set_data_values(self, values: list[str]) -> None:
        self._data_values = values
        self._data_pointer = 0

    def read_data(self) -> str:
        if self._data_pointer >= len(self._data_values):
            raise BasicError(42)  # OUT OF DATA
        val = self._data_values[self._data_pointer]
        self._data_pointer += 1
        return val

    def restore(self) -> None:
        self._data_pointer = 0

    # --- FN ---

    def def_fn(self, name: str, param: str, body: object) -> None:
        self._fn_defs[name] = (param, body)

    def get_fn(self, name: str) -> tuple[str, object]:
        if name not in self._fn_defs:
            raise BasicError(224)  # UNDEF'D FUNCTION
        return self._fn_defs[name]

    # --- CONT ---

    def save_cont_point(self, line_num: int, stmt_idx: int) -> None:
        self._cont_point = (line_num, stmt_idx)
        self._stopped = True

    def get_cont_point(self) -> tuple[int, int] | None:
        if self._program_modified or not self._stopped:
            return None
        return self._cont_point

    def clear_cont(self) -> None:
        self._cont_point = None
        self._stopped = False

    def mark_program_modified(self) -> None:
        self._program_modified = True

    @property
    def stopped(self) -> bool:
        return self._stopped


def _check_type_assignment(name: str, value: object) -> None:
    """Vérifie la compatibilité de type pour une assignation (RG-0007)."""
    if name.endswith("$"):
        if not isinstance(value, str):
            raise BasicError(163)  # TYPE MISMATCH
    else:
        if isinstance(value, str):
            raise BasicError(163)  # TYPE MISMATCH


def _to_integer(value: float | int) -> int:
    """Convertit en entier 16 bits signé (suffixe %, RG-0006)."""
    if isinstance(value, float):
        value = int(value)  # Tronquer, pas arrondir
    if value < -32768 or value > 32767:
        raise BasicError(53)  # ILLEGAL QUANTITY
    return value
