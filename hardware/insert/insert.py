"""The printed insert of the ectotherm camera trap: a FreeCAD script that writes STL files.

Run with FreeCAD's command line, from anywhere:

    freecadcmd hardware/insert/insert.py
    flatpak run --command=FreeCADCmd org.freecad.FreeCAD hardware/insert/insert.py

It writes the parts of every bucket in BUCKETS to stl/<bucket>/, each lying flat as it is printed,
with assembly.stl showing them in place (for looking at, not for printing). INSERT_BUCKETS, a
comma-separated list of names, limits it to some buckets.

The trap is an upturned bucket. Coordinates: z up from the ground, the passage along x from side A
(negative x) to side B, the fence meeting the bucket on the y axis. The passage floor lies on the
ground and reaches the openings cut in the bucket wall at both ends of the passage; walls on both
sides of the passage go up to the top of the bucket, so the two spaces beside the passage are
closed to animals and hold the electronics. Near each end a beam point carries beams at 4, 12 and
25 mm above the floor: laser modules in the wall on the +y side, photodiodes facing them in the
-y side. A bridge across the walls holds the camera, its infrared LEDs and the roof laser, at a
height set between 200 and 300 mm above the floor.
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import FreeCAD  # noqa: F401  (loads the document machinery MeshPart needs)
import MeshPart
import Part
from FreeCAD import Vector


@dataclass(frozen=True)
class Bucket:
    """A bucket, measured inside."""

    name: str
    rim_d: float  # diameter at the rim, the wide end, which stands on the ground
    base_d: float  # diameter at the base, the top of the upturned bucket
    height: float  # from rim to base


BUCKETS = {
    b.name: b
    for b in (
        Bucket("bucket-20l", rim_d=295.0, base_d=260.0, height=360.0),
        Bucket("bucket-25l", rim_d=315.0, base_d=280.0, height=390.0),
    )
}

# The passage, in mm.
PASSAGE_W = 150.0  # between the walls
FLOOR_T = 3.0  # floor thickness
FLOOR_EDGE_T = 0.6  # floor thickness at the openings, where it meets the ground
FLOOR_TAPER = 15.0  # length over which the floor thins towards the openings
OPENING_H = 100.0  # height of the openings cut in the bucket wall
CLEAR = 2.0  # gap between the insert and the bucket wall

# The beam walls: the lower part of the passage walls, thick enough for the beam sockets.
BEAM_WALL_T = 12.0
BEAM_WALL_H = 60.0  # above the floor's top
BEAM_HEIGHTS = (4.0, 12.0, 25.0)  # above the floor's top
BEAM_INSET = 20.0  # from each end of the passage to its beam point
APERTURE_D = 1.5  # opening on the passage side, so that each beam sees only its partner
LASER_SOCKET_D = 6.2  # a 6 mm laser diode module
PHOTODIODE_SOCKET_D = 5.2  # a 5 mm photodiode
SOCKET_DEPTH = BEAM_WALL_T - 2.0
SIDE_WINDOW = (100.0, 40.0, 10.0)  # length, height and height above the floor; +y wall only

# The upper walls, up to the top of the bucket.
UPPER_WALL_T = 3.0
CAMERA_RANGE = (200.0, 300.0)  # lens height above the floor's top
HOLE_STEP = 10.0  # the bridge is screwed on at any of these steps
RAIL_X = 25.0  # the bridge's screws, either side of the middle
CABLE_SLOT = (26.0, 3.0)  # length and height: a camera ribbon passes, an animal does not
BAY_GRID = 20.0  # holes on the walls' outer faces for boards and cells

# Parts.
M3 = 3.4  # clearance hole for an M3 screw
BRIDGE_L = 60.0  # along the passage
BRIDGE_T = 4.0
FLANGE_H = 30.0
CAMERA_HOLE_D = 16.0
LED_HOLE_D = 5.2
LED_RING_R = 22.0
SPLICE = (20.0, 40.0, 4.0)
FENCE_SLOT_W = 6.0
FENCE_CLAMP_H = 150.0
TEMPLATE_T = 0.8

# The printer.
BED = 256.0
BED_MARGIN = 3.0


class InsertError(Exception):
    """The bucket cannot take the insert."""


# --- Geometry helpers --------------------------------------------------------------------------


def box(x0, x1, y0, y1, z0, z1) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def hole_y(x, z, d, y0, y1) -> Part.Shape:
    """A round hole along y, from y0 to y1, centred at x and z."""
    return Part.makeCylinder(d / 2, y1 - y0, Vector(x, y0, z), Vector(0, 1, 0))


def hole_z(x, y, d, z0, z1) -> Part.Shape:
    return Part.makeCylinder(d / 2, z1 - z0, Vector(x, y, z0), Vector(0, 0, 1))


def inside(b: Bucket, clear: float = CLEAR) -> Part.Shape:
    """The space inside the bucket, less a gap to its wall."""
    r_rim, r_base = b.rim_d / 2 - clear, b.base_d / 2 - clear
    return Part.makeCone(r_rim, r_base, b.height - clear, Vector(0, 0, 0))


def radius_at(b: Bucket, z: float) -> float:
    return b.rim_d / 2 - (b.rim_d - b.base_d) / 2 * z / b.height - CLEAR


def passage_end(b: Bucket, z: float) -> float:
    """x of the passage's end at the walls' passage side, at height z."""
    return math.sqrt(radius_at(b, z) ** 2 - (PASSAGE_W / 2) ** 2)


def top(b: Bucket) -> float:
    return b.height - CLEAR


def check(b: Bucket) -> None:
    lens_top = FLOOR_T + CAMERA_RANGE[1] + BRIDGE_T + FLANGE_H
    if lens_top > top(b):
        raise InsertError(
            f"{b.name}: {b.height:.0f} mm is too low for the camera's range up to "
            f"{CAMERA_RANGE[1]:.0f} mm and its bridge; the bucket needs at least "
            f"{lens_top + CLEAR:.0f} mm inside"
        )
    if b.rim_d / 2 - CLEAR <= PASSAGE_W / 2 + BEAM_WALL_T + 20:
        raise InsertError(f"{b.name}: too narrow for a passage of {PASSAGE_W:.0f} mm")


# --- The parts in place ------------------------------------------------------------------------


def floor(b: Bucket) -> Part.Shape:
    """The passage floor and the strips the walls stand on, thinning towards the openings."""
    y = PASSAGE_W / 2 + BEAM_WALL_T
    r = b.rim_d / 2 - CLEAR
    strip = box(-r, r, -y, y, 0, FLOOR_T)
    rim = Part.makeCylinder(r, FLOOR_EDGE_T, Vector(0, 0, 0))
    taper = Part.makeCone(r, r - FLOOR_TAPER, FLOOR_T - FLOOR_EDGE_T, Vector(0, 0, FLOOR_EDGE_T))
    shape = strip.common(rim.fuse(taper))
    # Countersunk screws from below into each beam wall.
    for x in (-0.5, 0.5):
        for side in (-1, 1):
            xs = x * passage_end(b, 0) * 1.2
            ys = side * (PASSAGE_W / 2 + BEAM_WALL_T / 2)
            shape = shape.cut(hole_z(xs, ys, M3, -1, FLOOR_T + 1))
            shape = shape.cut(Part.makeCone(3.2, 1.7, 1.5, Vector(xs, ys, 0)))
    return shape


def beam_wall(b: Bucket, side: int) -> Part.Shape:
    """The lower wall on one side of the passage: +1 holds the lasers and the side window, -1
    the photodiodes."""
    y_in, y_out = side * PASSAGE_W / 2, side * (PASSAGE_W / 2 + BEAM_WALL_T)
    y0, y1 = min(y_in, y_out), max(y_in, y_out)
    z0, z1 = FLOOR_T, FLOOR_T + BEAM_WALL_H
    shape = box(-200, 200, y0, y1, z0, z1).common(inside(b))
    socket_d = LASER_SOCKET_D if side > 0 else PHOTODIODE_SOCKET_D
    x_point = passage_end(b, z0) - BEAM_INSET
    for x in (-x_point, x_point):
        for h in BEAM_HEIGHTS:
            z = FLOOR_T + h
            shape = shape.cut(hole_y(x, z, APERTURE_D, y0 - 1, y1 + 1))
            if side > 0:
                shape = shape.cut(hole_y(x, z, socket_d, y_out - SOCKET_DEPTH, y_out + 1))
            else:
                shape = shape.cut(hole_y(x, z, socket_d, y_out - 1, y_out + SOCKET_DEPTH))
    if side > 0:
        length, height, above = SIDE_WINDOW
        shape = shape.cut(
            box(-length / 2, length / 2, y0 - 1, y1 + 1, FLOOR_T + above, FLOOR_T + above + height)
        )
    # Screws from the floor below, and splice holes to the upper wall.
    for x in (-0.5, 0.5):
        xs = x * passage_end(b, 0) * 1.2
        shape = shape.cut(hole_z(xs, (y_in + y_out) / 2, 2.8, z0 - 1, z0 + 12))
    return shape.cut(_splice_holes(z1, y0, y1))


def _splice_holes(z_joint: float, y0: float, y1: float) -> Part.Shape:
    holes = []
    for x in (-80.0, 80.0):
        for dz in (-SPLICE[1] / 4, SPLICE[1] / 4):
            holes.append(hole_y(x, z_joint + dz, 2.8, y0 - 1, y1 + 1))
    return Part.makeCompound(holes)


def upper_wall(b: Bucket, side: int) -> Part.Shape:
    """The wall above the beam wall, up to the top of the bucket, with the bridge's holes, a
    camera cable slot and holes for boards and cells on its outer face."""
    y_in, y_out = side * PASSAGE_W / 2, side * (PASSAGE_W / 2 + UPPER_WALL_T)
    y0, y1 = min(y_in, y_out), max(y_in, y_out)
    z0, z1 = FLOOR_T + BEAM_WALL_H, top(b)
    shape = box(-200, 200, y0, y1, z0, z1).common(inside(b))
    cuts = []
    steps = int((CAMERA_RANGE[1] - CAMERA_RANGE[0]) / HOLE_STEP)
    for k in range(steps + 1):
        z = FLOOR_T + CAMERA_RANGE[0] + k * HOLE_STEP + BRIDGE_T + FLANGE_H / 2
        for x in (-RAIL_X, RAIL_X):
            cuts.append(hole_y(x, z, M3, y0 - 1, y1 + 1))
    slot_l, slot_h = CABLE_SLOT
    slot_z = FLOOR_T + sum(CAMERA_RANGE) / 2
    cuts.append(box(40, 40 + slot_l, y0 - 1, y1 + 1, slot_z, slot_z + slot_h))
    grid_x = [x for x in range(-140, 141, int(BAY_GRID)) if abs(x) > 50]
    for x in grid_x:
        for z in range(int(z0 + 20), int(z1 - 10), int(BAY_GRID)):
            cuts.append(hole_y(x, z, 2.8, y0 - 1, y1 + 1))
    shape = shape.cut(Part.makeCompound(cuts))
    return shape.cut(_splice_holes(z0, y0, y1)).common(inside(b))


def split_upper_wall(b: Bucket, wall: Part.Shape) -> list[list[Part.Shape]]:
    """The upper wall cut so that each piece fits the bed lying flat: in rows by height, and a
    row also in two halves where it is too long, with splice holes at each cut. Returns the rows
    from the bottom, each with one piece or its two halves (x < 0 first)."""
    z0, z1 = FLOOR_T + BEAM_WALL_H, top(b)
    count = max(1, math.ceil((z1 - z0) / (BED - 2 * BED_MARGIN - 10)))
    cuts = [z0 + (z1 - z0) * k / count for k in range(count + 1)]
    rows = []
    y0, y1 = wall.BoundBox.YMin, wall.BoundBox.YMax
    for lo, hi in zip(cuts, cuts[1:]):
        piece = wall.common(box(-200, 200, y0 - 1, y1 + 1, lo, hi))
        for z_joint in (lo, hi):
            if z0 < z_joint < z1:
                piece = piece.cut(_splice_holes(z_joint, y0, y1))
        if flat_turn(piece) is not None:
            rows.append([piece])
            continue
        # Two halves, joined by splice plates turned across the joint.
        holes = []
        for z in (lo + (hi - lo) / 3, lo + 2 * (hi - lo) / 3):
            for dx in (-SPLICE[1] / 4, SPLICE[1] / 4):
                holes.append(hole_y(dx, z, 2.8, y0 - 1, y1 + 1))
        piece = piece.cut(Part.makeCompound(holes))
        rows.append([piece.common(box(-200, 0, y0 - 1, y1 + 1, lo - 1, hi + 1)),
                     piece.common(box(0, 200, y0 - 1, y1 + 1, lo - 1, hi + 1))])  # fmt: skip
    return rows


def bridge(b: Bucket, lens_height: float) -> Part.Shape:
    """The camera bridge across the passage, its plate lens_height above the floor's top."""
    w = PASSAGE_W - 1.0
    z = FLOOR_T + lens_height
    plate = box(-BRIDGE_L / 2, BRIDGE_L / 2, -w / 2, w / 2, z, z + BRIDGE_T)
    flanges = [
        box(-BRIDGE_L / 2, BRIDGE_L / 2, s * w / 2 - (BRIDGE_T if s > 0 else 0),
            s * w / 2 + (0 if s > 0 else BRIDGE_T), z, z + BRIDGE_T + FLANGE_H)
        for s in (-1, 1)
    ]  # fmt: skip
    shape = plate.fuse(flanges[0]).fuse(flanges[1])
    cuts = [hole_z(0, 0, CAMERA_HOLE_D, z - 1, z + BRIDGE_T + 1)]
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        cuts.append(hole_z(LED_RING_R * math.cos(a), LED_RING_R * math.sin(a), LED_HOLE_D,
                           z - 1, z + BRIDGE_T + 1))  # fmt: skip
    cuts.append(hole_z(0, 45, LASER_SOCKET_D, z - 1, z + BRIDGE_T + 1))  # the roof laser
    for x in (-RAIL_X, RAIL_X):
        cuts.append(hole_y(x, z + BRIDGE_T + FLANGE_H / 2, M3, -w, w))
    return shape.cut(Part.makeCompound(cuts))


def window_plug(b: Bucket) -> Part.Shape:
    """Closes the side window until a mirror or a second camera is tried."""
    length, height, above = SIDE_WINDOW
    y0 = PASSAGE_W / 2
    plug = box(-length / 2 + 0.3, length / 2 - 0.3, y0, y0 + BEAM_WALL_T,
               FLOOR_T + above + 0.3, FLOOR_T + above + height - 0.3)  # fmt: skip
    lip = box(-length / 2 - 5, length / 2 + 5, y0 + BEAM_WALL_T, y0 + BEAM_WALL_T + 2,
              FLOOR_T + above - 5, FLOOR_T + above + height + 5)  # fmt: skip
    return plug.fuse(lip)


def splice_plate(step: float = 0.0) -> Part.Shape:
    """Joins two wall pieces on their outer faces, across the joint at z = 0; step thickens its
    upper half, where the upper wall's outer face lies further in than the beam wall's."""
    w, h, t = SPLICE
    plate = box(-w / 2, w / 2, 0, t, -h / 2, h / 2)
    if step:
        plate = plate.fuse(box(-w / 2, w / 2, -step, 0, 0, h / 2))
    for dz in (-h / 4, h / 4):
        plate = plate.cut(hole_y(0, dz, M3, -step - 1, t + 1))
    return plate


def fence_clamp() -> Part.Shape:
    """Holds a fence's end behind the slit cut in the bucket wall, so no gap is left beside the
    trap; glued or screwed to the bucket wall."""
    depth, wall = 30.0, 4.0
    body = box(0, depth + wall, -(FENCE_SLOT_W / 2 + wall), FENCE_SLOT_W / 2 + wall, 0,
               FENCE_CLAMP_H)  # fmt: skip
    slot = box(-1, depth, -FENCE_SLOT_W / 2, FENCE_SLOT_W / 2, -1, FENCE_CLAMP_H + 1)
    flange = box(-wall, 0, -(FENCE_SLOT_W / 2 + 20), FENCE_SLOT_W / 2 + 20, 0, FENCE_CLAMP_H)
    flange = flange.cut(box(-wall - 1, 1, -FENCE_SLOT_W / 2, FENCE_SLOT_W / 2, -1,
                            FENCE_CLAMP_H + 1))  # fmt: skip
    for z in (30.0, FENCE_CLAMP_H - 30.0):
        for y in (-(FENCE_SLOT_W / 2 + 12), FENCE_SLOT_W / 2 + 12):
            flange = flange.cut(Part.makeCylinder(M3 / 2, wall + 2, Vector(-wall - 1, y, z),
                                                  Vector(1, 0, 0)))  # fmt: skip
    return body.cut(slot).fuse(flange)


def template(outer: tuple[float, float], window: tuple[float, float]) -> Part.Shape:
    """A thin, flexible template laid on the bucket to mark a cut: trace inside its window."""
    (ow, oh), (ww, wh) = outer, window
    plate = box(-ow / 2, ow / 2, -oh / 2, oh / 2, 0, TEMPLATE_T)
    plate = plate.cut(box(-ww / 2, ww / 2, -wh / 2, wh / 2, -1, TEMPLATE_T + 1))
    # A notch in the middle of the bottom edge marks the centre line.
    return plate.cut(box(-1, 1, -oh / 2 - 1, -oh / 2 + 4, -1, TEMPLATE_T + 1))


# --- Printing ----------------------------------------------------------------------------------


TURNS = ((Vector(1, 0, 0), 0), (Vector(1, 0, 0), 90), (Vector(0, 1, 0), 90))


def flat_turn(shape: Part.Shape) -> tuple[Vector, float, float] | None:
    """The turn that lays the part on its lowest side, and the spin on the bed that fits it, or
    None when it does not fit the bed lying that way."""
    usable = BED - 2 * BED_MARGIN

    def turned(axis: Vector, angle: float) -> Part.Shape:
        copy = shape.copy()
        if angle:
            copy.rotate(Vector(0, 0, 0), axis, angle)
        return copy

    axis, angle = min(TURNS, key=lambda t: turned(*t).BoundBox.ZLength)
    points = [(v.x, v.y) for v in turned(axis, angle).tessellate(0.5)[0]]
    for spin in range(0, 90):
        a = math.radians(spin)
        xs = [x * math.cos(a) - y * math.sin(a) for x, y in points]
        ys = [x * math.sin(a) + y * math.cos(a) for x, y in points]
        if max(xs) - min(xs) <= usable and max(ys) - min(ys) <= usable:
            return axis, angle, spin
    return None


def lay_flat(shape: Part.Shape, name: str) -> Part.Shape:
    """The part laid on its lowest side and moved onto the bed; raises InsertError when it does
    not fit the bed that way."""
    turn = flat_turn(shape)
    if turn is None:
        raise InsertError(f"{name} does not fit a {BED:.0f} mm bed lying flat")
    axis, angle, spin = turn
    placed = shape.copy()
    if angle:
        placed.rotate(Vector(0, 0, 0), axis, angle)
    placed.rotate(Vector(0, 0, 0), Vector(0, 0, 1), spin)
    # The extent from the part's mesh points: the quick bounding box is loose around curves.
    points = placed.tessellate(0.05)[0]
    xs, ys, zs = [p.x for p in points], [p.y for p in points], [p.z for p in points]
    placed.translate(
        Vector(-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -min(zs))
    )
    return placed


def write_stl(shape: Part.Shape, path: Path) -> None:
    mesh = MeshPart.meshFromShape(
        Shape=shape, LinearDeflection=0.05, AngularDeflection=0.3, Relative=False
    )
    mesh.write(str(path))


def build(b: Bucket, out: Path) -> list[tuple[str, int]]:
    """Writes the bucket's parts to out; returns each file's name with how many to print."""
    check(b)
    out.mkdir(parents=True, exist_ok=True)
    lens = sum(CAMERA_RANGE) / 2
    rows = split_upper_wall(b, upper_wall(b, 1))
    upper = [piece for row in rows for piece in row]
    in_place = {
        "floor": floor(b),
        "beam-wall-lasers": beam_wall(b, 1),
        "beam-wall-photodiodes": beam_wall(b, -1),
        "bridge": bridge(b, lens),
        "window-plug": window_plug(b),
    }
    upper_names = {}
    for k, row in enumerate(rows, start=1):
        for half, piece in zip("ab" if len(row) == 2 else [""], row):
            upper_names[f"upper-wall-{k}{half}"] = piece
    in_place.update(upper_names)
    # The floor is printed in two halves, joined by the beam walls standing on both.
    floor_half = in_place["floor"].common(box(0, 400, -200, 200, -1, 10))
    printed = {
        "floor-half": (floor_half, 2),
        "beam-wall-lasers": (in_place["beam-wall-lasers"], 1),
        "beam-wall-photodiodes": (in_place["beam-wall-photodiodes"], 1),
        "bridge": (in_place["bridge"], 1),
        "window-plug": (in_place["window-plug"], 1),
        # Two plates per joint and side: beam wall to upper wall, between rows of the upper
        # wall, and across a row cut in halves.
        "splice-plate-step": (splice_plate(BEAM_WALL_T - UPPER_WALL_T), 4),
        "splice-plate": (
            splice_plate(),
            4 * (len(rows) - 1) + 4 * sum(1 for row in rows if len(row) == 2),
        ),
        "fence-clamp": (fence_clamp(), 2),
        "template-opening": (template((PASSAGE_W + 20, OPENING_H + 20), (PASSAGE_W, OPENING_H)), 1),
        "template-fence-slit": (template((FENCE_SLOT_W + 24, FENCE_CLAMP_H + 20),
                                         (FENCE_SLOT_W, FENCE_CLAMP_H)), 1),  # fmt: skip
        "template-cable-hole": (template((40, 40), (20, 20)), 1),
    }
    for name, piece in upper_names.items():
        printed[name] = (piece, 2)  # one per side; the -y side takes the same piece turned over

    files = []
    for name, (shape, count) in printed.items():
        if not shape.isValid() or shape.Volume <= 0:
            raise InsertError(f"{b.name}: {name} is not a valid solid")
        write_stl(lay_flat(shape, f"{b.name}: {name}"), out / f"{name}.stl")
        files.append((f"{name}.stl", count))

    # The whole insert in place, for looking at.
    whole = list(in_place.values())
    whole += [s.mirror(Vector(0, 0, 0), Vector(0, 1, 0)) for s in upper]
    outside = Part.makeCompound(whole).cut(inside(b, clear=CLEAR - 0.5))
    if outside.Volume > 1.0:
        raise InsertError(f"{b.name}: the insert reaches through the bucket wall")
    write_stl(Part.makeCompound(whole), out / "assembly.stl")
    return files


def main() -> int:
    here = Path(__file__).resolve().parent
    wanted = os.environ.get("INSERT_BUCKETS")
    names = [n.strip() for n in wanted.split(",")] if wanted else list(BUCKETS)
    for name in names:
        if name not in BUCKETS:
            print(f"insert: unknown bucket {name}; known: {', '.join(BUCKETS)}")
            return 1
        try:
            files = build(BUCKETS[name], here / "stl" / name)
        except InsertError as error:
            print(f"insert: {error}")
            return 1
        print(f"{name}: " + ", ".join(f"{count} x {f}" for f, count in files))
    return 0


if __name__ in ("__main__", "insert"):
    status = main()
    if status:
        sys.exit(status)
