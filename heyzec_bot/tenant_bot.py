from dataclasses import dataclass, field


@dataclass
class TenantBot:
    name: str
    handlers: list[object] = field(default_factory=lambda: [])


