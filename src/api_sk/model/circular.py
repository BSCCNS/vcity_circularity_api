"""Compute the weighted sum indicator."""

from decimal import Decimal

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated, Self

from api_sk.core.config import settings

Weight = Annotated[
    Decimal, Field(ge=0, le=1, strict=False, allow_inf_nan=False, decimal_places=2)
]
Indicator = Annotated[
    Decimal, Field(ge=0, le=1, strict=False, allow_inf_nan=False, decimal_places=2)
]


class kpiWeightsD(BaseModel):
    D1: Weight = Decimal("1")

    @model_validator(mode="after")
    def sum_kpi_weights_d(self, tolerance=settings.TOLERANCE) -> Self:
        if abs(self.D1 - Decimal("1")) >= Decimal(tolerance):
            raise ValueError("The sum of the param weights is not 1.")
        return self


class kpiWeightsECR(BaseModel):
    ECR1: Weight = Decimal("0.3")
    ECR2: Weight = Decimal("0.2")
    ECR3: Weight = Decimal("0.3")
    ECR4: Weight = Decimal("0.2")

    @model_validator(mode="after")
    def sum_kpi_weights_ecr(self, tolerance=settings.TOLERANCE) -> Self:
        if abs(self.ECR1 + self.ECR2 + self.ECR3 + self.ECR4 - Decimal("1")) >= Decimal(
            tolerance
        ):
            raise ValueError("The sum of the param weights is not 1.")
        return self


class kpiWeightsM(BaseModel):
    M1: Weight = Decimal("0.2")
    M2: Weight = Decimal("0.2")
    M3: Weight = Decimal("0.2")
    M4: Weight = Decimal("0.2")
    M5: Weight = Decimal("0.2")

    @model_validator(mode="after")
    def sum_kpi_weights_m(self, tolerance=settings.TOLERANCE) -> Self:
        if abs(
            self.M1 + self.M2 + self.M3 + self.M4 + self.M5 - Decimal("1")
        ) >= Decimal(tolerance):
            raise ValueError("The sum of the param weights is not 1.")
        return self


class kpiWeightsW(BaseModel):
    W1: Weight = Decimal("0.4")
    W2: Weight = Decimal("0.4")
    W3: Weight = Decimal("0.2")

    @model_validator(mode="after")
    def sum_kpi_weights_w(self, tolerance=settings.TOLERANCE) -> Self:
        if abs(self.W1 + self.W2 + self.W3 - Decimal("1")) >= Decimal(tolerance):
            raise ValueError("The sum of the param weights is not 1.")
        return self


class AreaWeight(BaseModel):
    area_weight: Weight = Decimal("1.0")
    kpi_weights: kpiWeightsD | kpiWeightsECR | kpiWeightsM | kpiWeightsW


class CCIWeights(BaseModel):
    D: AreaWeight = AreaWeight(
        area_weight=Decimal("0.1"), kpi_weights=kpiWeightsD(D1=Decimal("1.0"))
    )
    ECR: AreaWeight = AreaWeight(
        area_weight=Decimal("0.3"),
        kpi_weights=kpiWeightsECR(
            ECR1=Decimal("0.3"),
            ECR2=Decimal("0.2"),
            ECR3=Decimal("0.3"),
            ECR4=Decimal("0.2"),
        ),
    )
    M: AreaWeight = AreaWeight(
        area_weight=Decimal("0.3"),
        kpi_weights=kpiWeightsM(
            M1=Decimal("0.2"),
            M2=Decimal("0.2"),
            M3=Decimal("0.2"),
            M4=Decimal("0.2"),
            M5=Decimal("0.2"),
        ),
    )
    W: AreaWeight = AreaWeight(
        area_weight=Decimal("0.3"),
        kpi_weights=kpiWeightsW(
            W1=Decimal("0.4"), W2=Decimal("0.4"), W3=Decimal("0.2")
        ),
    )

    @model_validator(mode="after")
    def sum_area_weights(self, tolerance=settings.TOLERANCE) -> Self:
        if abs(
            self.D.area_weight
            + self.ECR.area_weight
            + self.M.area_weight
            + self.W.area_weight
            - Decimal("1")
        ) >= Decimal(tolerance):
            raise ValueError("The sum of the param weights is not 1.")
        return self


class AreaKPIs(BaseModel):
    D: Indicator = Decimal("0.0")
    ECR: Indicator = Decimal("0.0")
    M: Indicator = Decimal("0.0")
    W: Indicator = Decimal("0.0")


class DistrictIndicators(BaseModel):
    area_kpis: AreaKPIs = AreaKPIs(
        D=Decimal("0.0"), ECR=Decimal("0.0"), M=Decimal("0.0"), W=Decimal("0.0")
    )
    cci: Indicator = Decimal("0.0")


class District(BaseModel):
    id: str
    indicators: DistrictIndicators = DistrictIndicators(
        area_kpis=AreaKPIs(
            D=Decimal("0.0"), ECR=Decimal("0.0"), M=Decimal("0.0"), W=Decimal("0.0")
        ),
        cci=Decimal("0.0"),
    )


class Districts(BaseModel):
    districts: list[District]

    @model_validator(mode="after")
    def diferent_ids(self) -> Self:
        if len(set(district.id for district in self.districts)) != len(self.districts):
            raise ValueError("IDs are not different.")
        return self
