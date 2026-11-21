# The printed insert

`insert.py` is a FreeCAD script that generates the insert for an upturned bucket. It writes the
parts as STL files, each lying flat as it is printed and checked to fit a 256 × 256 mm bed, to
`stl/<bucket>/`. `stl/<bucket>/assembly.stl` shows the whole insert in place, for looking at, not
for printing.

## Running it

```
freecadcmd hardware/insert/insert.py
flatpak run --command=FreeCADCmd org.freecad.FreeCAD hardware/insert/insert.py
```

The buckets are listed in `BUCKETS` at the top of the script, measured inside: the diameter at the
rim (the wide end, which stands on the ground), the diameter at the base, and the height. Add yours
there. `INSERT_BUCKETS=bucket-20l` limits a run to some of them. A bucket too low for the camera's
range of 200 to 300 mm above the floor, such as a 10 litre one, is refused.

| Bucket | Inside: rim, base, height |
|---|---|
| `bucket-20l` | 295, 260, 360 mm |
| `bucket-25l` | 315, 280, 390 mm |

## What to print

The script prints the number of each part, such as `2 x floor-half.stl`. For the 20 litre bucket:

| Part | Number | What it is |
|---|---|---|
| `floor-half` | 2 | the passage floor, thinning to 0.6 mm at the openings so it meets the ground |
| `beam-wall-lasers` | 1 | the lower wall on the +y side, with sockets for 6 mm laser modules and the side window |
| `beam-wall-photodiodes` | 1 | the lower wall on the -y side, with sockets for 5 mm photodiodes |
| `upper-wall-1`, `upper-wall-2` | 2 each | the walls above, up to the top of the bucket; the second of each is fitted turned over on the other side |
| `splice-plate-step` | 4 | joins a beam wall to the upper wall above it |
| `splice-plate` | 4 | joins the pieces of the upper walls |
| `bridge` | 1 | carries the camera, four infrared LEDs and the roof laser across the passage |
| `window-plug` | 1 | closes the side window until a mirror or a second camera is tried |
| `fence-clamp` | 2 | holds a fence end behind the slit cut in the bucket wall |
| `template-opening`, `template-fence-slit`, `template-cable-hole` | 1 each | thin templates for marking the cuts in the bucket |

A larger bucket can need the upper walls in more pieces (such as `upper-wall-1a` and `-1b`) and
more splice plates; the script's count says how many.

## Putting it together

1. Mark and cut the bucket with the templates: a passage opening 150 mm wide and 100 mm high at the
   rim on two opposite sides, a fence slit halfway between them on each side, and a cable hole in
   one of the two spaces beside the passage. The notch on each template marks its centre line.
2. Screw the beam walls onto the floor halves from below with countersunk M3 screws; the walls
   join the two halves.
3. Stand the upper walls on the beam walls and join them with the splice plates on the outer
   faces, M3 screws into the walls.
4. Screw the bridge between the walls at the camera height being tested, M3 through the walls
   into the bridge's flanges; the holes step by 10 mm from 200 to 300 mm above the floor.
5. Glue or screw the fence clamps behind the fence slits.
6. Lower the bucket over the insert, so the passage openings line up with the passage.

The spaces beside the passage are closed to animals and hold the electronics; the holes on the
upper walls' outer faces take boards and cell holders. For the prototype, the cables leave through
the cable hole, and the camera's ribbon reaches the bridge through the slot in an upper wall.
