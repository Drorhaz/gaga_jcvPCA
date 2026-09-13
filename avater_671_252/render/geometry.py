"""Project the 3D reference pose to 2D avatar coordinates for drawing.

Motive skeleton positions are Y-up in millimeters. A frontal avatar uses the
(X, Y) plane (X = left/right, Y = height); Z (depth) is dropped. Joint tokens
match the ``parent_joint``/``child_joint`` tokens in the tables.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pose2D:
    participant: str
    points: dict[str, tuple[float, float]]   # joint token -> (x, y)

    def has(self, joint: str) -> bool:
        return joint in self.points

    def segment(self, parent: str, child: str):
        """Return ((x0, y0), (x1, y1)) for an edge, or None if a joint is missing."""
        if parent in self.points and child in self.points:
            return self.points[parent], self.points[child]
        return None

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        xs = [p[0] for p in self.points.values()]
        ys = [p[1] for p in self.points.values()]
        return min(xs), max(xs), min(ys), max(ys)


def pose_to_2d(pose: dict) -> Pose2D:
    """Frontal (X, Y) projection of a reference-pose dict."""
    joints = pose.get("joints", {})
    points: dict[str, tuple[float, float]] = {}
    for token, coords in joints.items():
        if coords is None or len(coords) < 2:
            continue
        x, y = coords[0], coords[1]
        if x is None or y is None:
            continue
        points[token] = (float(x), float(y))
    return Pose2D(participant=str(pose.get("participant", "")), points=points)
