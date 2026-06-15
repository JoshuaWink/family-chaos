"""Simulation report returned by the scheduling game engine."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SimulationReport:
    """Validation result and conflict details for a candidate schedule."""

    is_valid: bool
    conflicts: List[Dict[str, str]]
