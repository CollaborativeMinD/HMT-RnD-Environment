"""Generic lifecycle declarations; stage ordering grants no execution authority."""
from typing import Literal

Stage = Literal[
    "CMAD1", "CMAD2", "CMAD3", "PMCT1", "PMCT2", "PMCT3",
    "DOKE1", "DOKE2", "DOKE3", "MR1", "MR2", "MR3",
    "CSSI1", "CSSI2", "CSSI3", "IIEA1", "IIEA2", "IIEA3",
    "B1", "B2", "B3", "B4", "B5", "OPS1", "OPS2", "OPS3",
]
STAGES: tuple[Stage, ...] = (
    "CMAD1", "CMAD2", "CMAD3", "PMCT1", "PMCT2", "PMCT3",
    "DOKE1", "DOKE2", "DOKE3", "MR1", "MR2", "MR3",
    "CSSI1", "CSSI2", "CSSI3", "IIEA1", "IIEA2", "IIEA3",
    "B1", "B2", "B3", "B4", "B5", "OPS1", "OPS2", "OPS3",
)
ROLE_CEILINGS = {"rrca": "INVESTIGATE_ONLY", "missionassurance": "EVALUATE_ONLY",
                 "hmtmissionassurance": "EVALUATE_ONLY"}


def lane(stage: Stage) -> str:
    return "Build" if stage.startswith("B") else stage.rstrip("123")


def predecessor(stage: Stage) -> Stage | None:
    index = STAGES.index(stage)
    return STAGES[index - 1] if index else None
