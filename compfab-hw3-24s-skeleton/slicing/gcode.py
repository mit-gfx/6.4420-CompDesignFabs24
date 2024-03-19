import numpy as np

HEADER_LINES = [
    "G28",  # Home head
    "G90",  # Absolute positioning (for relative, set G91)
    "M106 S255",  # Fan on
    "M109 S190 T0",  # Heat head to 190 and wait
    "M190 S50",  # Heat bed to 50 and wait
]

FOOTER_LINES = [
    "M104 S0",  # Cool hot end
    "M140 S0",  # Cool print bed
    "M107",  # Fan off
    "G1 X0 Y180 F9000",  # Retract bed
]


class GCodeConverter:
    def __init__(self, speed):
        self.speed = speed
        self.extruded_amount = 1.0

    def move_to_position(self, target: np.ndarray) -> str:
        return f"G0 X{target[0]:.3f} Y{target[1]:.3f} Z{target[2]:.3f} F{self.speed}"

    def extrude_single_segment(self, p0: np.ndarray, p1: np.ndarray) -> str:
        extrude = self.extruded_amount + (np.linalg.norm(p1 - p0) * 0.5)
        self.extruded_amount = extrude
        return f"G1 X{p1[0]:.3f} Y{p1[1]:.3f} Z{p1[2]:.3f} E{extrude:.3f} F{self.speed}"

    def extrude_segment(self, targets: list[np.ndarray]) -> list[str]:
        lines = []
        last_target = targets[0]
        for target in targets[1:]:
            lines.append(self.extrude_single_segment(last_target, target))
            last_target = target
        lines.append("G92 E0")
        self.extruded_amount = 0
        return lines


def write_gcode_lines(file, lines: list[str]):
    file.writelines([line + " ;\n" for line in lines])


def convert_to_gcode(output_file_name: str, contours: list[list[list[np.ndarray]]]):
    machine = GCodeConverter(speed=600)  # mm / min

    lines = []
    lines.extend(HEADER_LINES)
    for layer in contours:
        for contour in layer:
            lines.append(machine.move_to_position(contour[0]))
            lines.extend(machine.extrude_segment(contour))
            lines.append(machine.extrude_single_segment(contour[-1], contour[0]))
    lines.extend(FOOTER_LINES)

    with open(output_file_name, "w") as file:
        write_gcode_lines(file, lines)
        print(f"Successfully wrote GCode to {output_file_name} [{len(lines)} lines]")


def write_contours(output_file_name: str, contours: list[list[list[np.ndarray]]]):
    lines = []
    for layer in contours:
        contours_text = []
        for contour in layer:
            vertex_text = []
            for vertex in contour:
                vertex_text.append(f"{vertex[0]:.3f} {vertex[1]:.3f} {vertex[2]:.3f}")
            contours_text.append(",".join(vertex_text))
        lines.append(";".join(contours_text))

    with open(output_file_name, "w") as file:
        file.writelines([line + "\n" for line in lines if len(line) > 0])
        print(f"Saved contour information to {output_file_name} [{len(lines)} lines]")


def load_contours(input_file_name: str) -> list[list[list[np.ndarray]]]:
    file = open(input_file_name, "r")
    lines = file.readlines()
    file.close()

    def parse_vertex(vertex, i, j, k):
        try:
            return np.array([float(coord) for coord in vertex.split(" ")])
        except:
            print(f"Failed to parse vertex: {vertex} ({i},{j},{k})")
            raise Exception()

    contours = [
        [
            [parse_vertex(vertex, i, j, k) for (k, vertex) in enumerate(contour.split(","))]
            for (j, contour) in enumerate(layer.split(";"))
        ]
        for (i, layer) in enumerate(lines)
        if len(layer) > 1
    ]
    return contours
