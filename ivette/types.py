from dataclasses import dataclass


@dataclass
class Step:
    step: int
    energy: float
    delta_e: float
    gmax: float
    grms: float
    xrms: float
    xmax: float
    walltime: float


@dataclass
class SystemInfo:
    system_id: str
    system: str
    node: str
    release: str
    version: str
    machine: str
    processor: str
    ntotal: int
