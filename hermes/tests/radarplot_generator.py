import matplotlib
from io import BytesIO

matplotlib.use("Agg")  # Must be before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import math

from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


def radar_factory(num_vars, frame="circle"):
    """
    Create a radar chart with `num_vars` Axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding Axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):

        def transform_path_non_affine(self, path):
            # Paths with non-unit interpolation steps correspond to gridlines,
            # in which case we force interpolation (to defeat PolarTransform's
            # autoconversion to circular arcs).
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):

        name = "radar"
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location("N")

        def set_rgrids(self, radii, labels=None, **kwargs):
            # Override set_rgrids to position labels at fixed angle and distance
            self.set_ylim(0, np.max(radii))
            gridlines = super().set_rgrids(radii, labels=[""] * len(radii), **kwargs)[0]

            # Remove any existing grid labels
            for label in self.yaxis.get_ticklabels():
                label.set_visible(False)

            # Add labels at the specified angle
            for radius in radii:
                radius45 = radius / np.sqrt(2)  # Adjust for 45-degree angle
                theta = np.deg2rad(45)

                # Calculate position in data coordinates
                x = theta  # * np.cos(theta)
                y = radius45  # * np.sin(theta)

                # Add small offset to prevent overlap with grid lines
                offset = 1
                y += offset

                self.text(x, y, str(int(radius)), rotation=45)

            return gridlines, []

        def fill(self, *args, closed=True, **kwargs):
            # Override fill so that line is closed by default
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            # Override plot so that line is closed by default
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            # Get the default theta locations
            angles = np.degrees(theta)

            # Remove any existing theta labels
            self.set_thetagrids([], [])

            for angle, label in zip(angles, labels):

                angle_rad = np.radians(angle)

                pad = 21.5
                x = angle_rad
                y = pad

                if angle > 45 and angle < 135:
                    ha = "right"
                elif angle > 225 and angle < 315:
                    ha = "left"
                else:
                    ha = "center"

                self.text(
                    x,
                    y,
                    label,
                    rotation=0,
                    transform=self.transData,
                    ha=ha,
                    va="center",
                )

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == "circle":
                return Circle((0.5, 0.5), 0.5)
            elif frame == "polygon":
                return RegularPolygon((0.5, 0.5), num_vars, radius=0.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == "circle":
                return super()._gen_axes_spines()
            elif frame == "polygon":
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(
                    axes=self,
                    spine_type="circle",
                    path=Path.unit_regular_polygon(num_vars),
                )
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(
                    Affine2D().scale(0.5).translate(0.5, 0.5) + self.transAxes
                )
                return {"polar": spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def generate_radar_plot_from_scores(
    speed, endurance, agility, strength, historical_results=None
):
    # Set up the data
    categories = ["Speed", "Endurance", "Agility", "Strength"]
    current_scores = [speed, endurance, agility, strength]

    # Create figure and polar subplot
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection="polar"))

    # Number of variables
    num_vars = len(categories)

    # Compute angle for each axis
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]

    # Plot current scores
    values = current_scores + [current_scores[0]]
    ax.plot(angles, values, "o-", linewidth=2, label="Current", color="blue")
    ax.fill(angles, values, alpha=0.25, color="blue")

    # Plot historical results if available
    colors = ["red", "green"]  # Colors for previous results
    if historical_results:
        for idx, hist_result in enumerate(
            historical_results[:2]
        ):  # Limit to 2 historical results
            hist_scores = [
                hist_result.speed_score or 0,  # Handle None values
                hist_result.endurance_score or 0,
                hist_result.agility_score or 0,
                hist_result.strength_score or 0,
            ]
            hist_scores += [hist_scores[0]]  # Close the polygon
            ax.plot(
                angles,
                hist_scores,
                "o-",
                linewidth=2,
                label=f'Test {hist_result.test_date.strftime("%Y-%m-%d")}',
                color=colors[idx],
            )
            ax.fill(angles, hist_scores, alpha=0.1, color=colors[idx])

    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)

    # Set chart properties
    ax.set_ylim(0, 20)
    plt.grid(True)

    # Add legend
    plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

    # Save plot to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
    buffer.seek(0)
    plt.close()

    return buffer
