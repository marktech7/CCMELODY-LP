from typing import *

from pydantic import BaseModel, Field


class ItemInfo(BaseModel):
    """
    None model

    """

    uuid: Optional[str] = Field(alias="uuid", default=None)

    version: Optional[int] = Field(alias="version", default=None)

    created: Optional[str] = Field(alias="created", default=None)

    updated: Optional[str] = Field(alias="updated", default=None)
