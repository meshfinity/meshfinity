from __future__ import annotations

from typing import List

from .base import BaseSession

sessions_class: List[type[BaseSession]] = []
sessions_names: List[str] = []

from .silueta import SiluetaSession

sessions_class.append(SiluetaSession)
sessions_names.append(SiluetaSession.name())
