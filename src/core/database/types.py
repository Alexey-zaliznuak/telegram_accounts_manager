from pydantic import BaseModel
from sqlalchemy import ColumnExpressionArgument

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from infrastructure.database.filtering import BaseFilterModel


type Data = dict | BaseModel
type Where = list[ColumnExpressionArgument[bool]] | ColumnExpressionArgument[bool]
type ConvertibleToWhere = Where | BaseFilterModel | True | None | list[ConvertibleToWhere]
