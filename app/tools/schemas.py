from typing import List, Optional

from pydantic import BaseModel, Field


class CampaignRecentParams(BaseModel):  # type: ignore[misc]
    account_id: str
    num_campaigns: int = Field(default=10)


class CampaignLookupParams(BaseModel):  # type: ignore[misc]
    account_id: str
    campaign_names: Optional[List[str]] = Field(default=None)
    campaign_ids: Optional[List[str]] = Field(default=None)


class KPIQueryArgs(BaseModel):  # type: ignore[misc]
    account_id: str
    campaign_id: Optional[List[str]] = ["ALL"]
    start_date: str = Field(default="1970-01-01")
    end_date: str = Field(default="2027-01-01")


class AggregateKPIQueryArgs(BaseModel):  # type: ignore[misc]
    account_id: str
    start_date: str = Field(default="1970-01-01")
    end_date: str = Field(default="2027-01-01")


class AnalyseDataInput(BaseModel):  # type: ignore[misc]
    query: str = Field(description="Natural language question about the data")
    df_data: str = Field(default="", description="DataFrame data as CSV string")
