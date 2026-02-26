from typing import Annotated
from uuid import UUID

from pydantic import BeforeValidator

# Coerce UUID objects to strings for JSON responses.
StrUUID = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, UUID) else v)]
