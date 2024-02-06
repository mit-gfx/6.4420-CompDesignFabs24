
import svgwrite
from svgwrite import mm, Drawing
import json
from typing import TypedDict, Union, cast
from pathlib import Path
from typeguard import typechecked
import cairosvg
import fire


class Room(TypedDict):
    label: str
    width: int
    height: int
    offsetx: int
    offsety: int


COLORS = {
    "Bedroom": "lightblue",
    "Bathroom": "lavender",  # changed from lightgray to make it distinct
    "Kitchen": "lightgreen",
    "LivingRoom": "lightyellow",
    "Closet": "lightpink",
    "Passageway": "lightcoral",  # changed from lightgray to make it distinct
    "Foyer": "lightsalmon",  # changed from lightgray to make it distinct
    "LaundryRoom": "lightgray",
    "DinningRoom": "lightskyblue",
}


@typechecked
def draw_room(dwg: Drawing, room: Room) -> None:
    """Helper function to draw each room."""
    room_color = COLORS.get(room["label"], "white")

    # Create rectangle for room
    dwg.add(
        dwg.rect(
            (room["offsetx"] * mm, room["offsety"] * mm),
            (room["width"] * mm, room["height"] * mm),
            stroke=svgwrite.rgb(0, 0, 0, "%"),
            fill=room_color,
        )
    )

    # Label room with name and dimensions
    # Label room with name
    dwg.add(
        dwg.text(
            room["label"],
            insert=(
                (room["offsetx"] + room["width"] / 2) * mm,
                (room["offsety"] + room["height"] / 2 - 0.5) * mm,
            ),  # Move up slightly for label
            text_anchor="middle",
            font_size=0.75 * mm,
        )
    )

    # Label room with dimensions
    room_dimensions = f"({room['width']}ft x {room['height']}ft)"
    dwg.add(
        dwg.text(
            room_dimensions,
            insert=(
                (room["offsetx"] + room["width"] / 2) * mm,
                (room["offsety"] + room["height"] / 2 + 0.5) * mm,
            ),  # Move down slightly for dimensions
            text_anchor="middle",
            font_size=0.75 * mm,
        )
    )


@typechecked
def draw_border(dwg: Drawing, room: Room) -> None:
    """Helper function to draw each room."""
    stroke_color = COLORS.get(room["label"], "black")
    # Create rectangle for room
    dwg.add(
        dwg.rect(
            (room["offsetx"] * mm, room["offsety"] * mm),
            (room["width"] * mm, room["height"] * mm),
            stroke="black",
            fill="none",
            stroke_width=1,
        )
    )


@typechecked
def generate_floor_plan(filename: Union[str, Path], output: Union[str, Path]):
    """
    Generates a PNG image of floor plans from a JSON file.
    """
    filename = Path(filename)
    assert filename.exists(), f"{filename} does not exist"
    rooms = cast(list[Room], json.loads(filename.read_text()))

    # Create SVG drawing
    W = max(room["offsetx"] + room["width"] for room in rooms)
    H = max(room["offsety"] + room["height"] for room in rooms)
    dwg = svgwrite.Drawing(str(output), size=(f"{W}mm", f"{H}mm"), profile="tiny")

    # Draw each room
    for room in rooms:
        draw_room(dwg, room)
    for room in rooms:
        draw_border(dwg, room)

    # Save the drawing
    # dwg.save()
    cairosvg.svg2png(dwg.tostring(), dpi=600, write_to=str(output))

    # Check total area
    total_area = sum([room["width"] * room["height"] for room in rooms])
    print(f"Area: {total_area} sq ft.")


if __name__ == "__main__":
    fire.Fire(generate_floor_plan)
