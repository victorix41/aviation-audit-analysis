"""Structured result for executive management insights."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutiveInsights:
    """Rule-based observations and recommendations."""

    observations: tuple[str, ...]
    recommendations: tuple[str, ...]

    @property
    def has_observations(self) -> bool:
        """Return whether any observations were generated."""

        return bool(self.observations)

    @property
    def has_recommendations(self) -> bool:
        """Return whether any recommendations were generated."""

        return bool(self.recommendations)
