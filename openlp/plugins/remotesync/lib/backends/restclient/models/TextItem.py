from typing import *

from pydantic import BaseModel, Field


class TextItem(BaseModel):
    """
    None model

    """

    uuid: Optional[str] = Field(alias="uuid", default=None)

    version: Optional[int] = Field(alias="version", default=None)

    created: Optional[str] = Field(alias="created", default=None)

    updated: Optional[str] = Field(alias="updated", default=None)

    title: Optional[str] = Field(alias="title", default=None)

    itemxml: Optional[str] = Field(alias="itemxml", default=None)
