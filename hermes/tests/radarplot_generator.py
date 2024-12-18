import matplotlib

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
    """
    Generate a radar plot from athlete test scores.

    Parameters
    ----------
    speed : float
        Speed score (0-20)
    endurance : float
        Endurance score (0-20)
    agility : float
        Agility score (0-20)
    strength : float
        Strength score (0-20)
    historical_results : list of dict, optional
        List of historical results, each containing speed, endurance, agility, and strength scores

    Returns
    -------
    BytesIO
        Buffer containing the PNG image of the radar plot
    """
    theta = radar_factory(4, frame="polygon")

    # Create plot
    fig, ax = plt.subplots(figsize=(7, 6), subplot_kw=dict(projection="radar"))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    spoke_labels = ["Speed", "Endurance", "Agility", "Strength"]
    ax.set_ylim(0, 20)
    ax.set_rgrids([5, 10, 15, 20])
    ax.set_varlabels(spoke_labels)

    # Plot current data
    current_data = [speed, endurance, agility, strength]
    ax.plot(theta, current_data, color="b", label="Current", linewidth=2)
    ax.fill(theta, current_data, color="b", alpha=0.25)

    # Plot historical data if provided
    if historical_results:
        colors = ["r", "g"]  # Colors for historical results
        for idx, result in enumerate(historical_results):
            historical_data = [
                result.speed_score,
                result.endurance_score,
                result.agility_score,
                result.strength_score,
            ]
            date_str = result.test_date.strftime("%Y-%m-%d")
            ax.plot(
                theta,
                historical_data,
                color=colors[idx],
                label=f"Previous ({date_str})",
                linestyle="--",
                alpha=0.7,
            )
            ax.fill(theta, historical_data, color=colors[idx], alpha=0.1)

    ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

    # Save to bytes buffer
    from io import BytesIO

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=300)
    plt.close()
    buf.seek(0)
    return buf


# def example_data():
#     data = [
#         [  # FIXME: this is counterclockwise
#             "Strength",
#             "Speed",
#             "Endurance",
#             "Mobility",
#         ],
#         (
#             "tst",
#             [
#                 [20, 15, 10, 5],
#                 [12, 3, 6, 17],
#                 [13, 6, 7, 10],
#             ],
#         ),
#     ]
#     return data


# theta = radar_factory(4, frame="polygon")

# data = example_data()
# spoke_labels = data.pop(0)

# fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection="radar"))
# fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

# ax.set_ylim(0, 20)
# ax.set_rgrids([5, 10, 15, 20])


# ax.set_varlabels(spoke_labels)


# case_data = data[0]
# case_name = case_data[0]
# all_data = np.array(case_data[1])

# colors = ["b", "r", "g"]
# labels = ["Line 1", "Line 2", "Line 3"]

# for d, color, label in zip(all_data, colors, labels):
#     ax.plot(theta, d, color=color, label=label)
#     ax.fill(theta, d, color=color, alpha=0.25)

# ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

# plt.show()
