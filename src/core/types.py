from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

# Kernel compartido: los montos se manejan como Decimal (precisión exacta, nunca float)
# y en las respuestas JSON se envían como número.
Dinero = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
