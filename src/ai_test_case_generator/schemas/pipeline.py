from pydantic import BaseModel

from ai_test_case_generator.schemas.critic import CritiqueReport
from ai_test_case_generator.schemas.evidence import EvidenceReport, GateResult
from ai_test_case_generator.schemas.generator import GeneratorOutput
from ai_test_case_generator.schemas.judge import JudgeOutput


class PipelineResult(BaseModel):
    generator_output: GeneratorOutput
    critique: CritiqueReport
    evidence: EvidenceReport
    judge_output: JudgeOutput
    gate: GateResult
