from enum import Enum
from typing import Any, TypeVar, Union

from pydantic import BaseModel, ConfigDict
from typing_extensions import Literal


class ApiBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        use_enum_values=True,
        protected_namespaces=(),
        validate_assignment=True,
        allow_inf_nan=False,
        validate_default=True,
    )

    def model_dump(
        self,
        *,
        mode: Union[Literal["json", "python"], str] = "python",
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        # exclude_none -> change from False to True
        exclude_none: bool = True,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )


E = TypeVar("E", bound=Enum)
EnumLike = Union[str, E]
EnumLikeList = list[Union[str, E]]
EnumLikeOrEnumLikeList = Union[EnumLike[E], EnumLikeList[E]]

D = TypeVar("D", bound=BaseModel)
ModelLike = Union[dict, D]
