# Sample notes

This folder holds examination artifacts only. Full raw CSVs remain under `data/raw_markers/` and `data/raw_skeleton/`.

Header layout (both export types):

- Row 0: metadata key/value pairs (Format Version, Take Name, frame rate, units, …)
- Row 1: `,Type,Marker,Marker,…` or `,Type,Bone,Bone,…,Marker,Marker,…`
- Row 2: marker/bone names
- Row 3: IDs
- Row 4: Parent
- Row 5: Position labels
- Row 6: `Frame,Time (Seconds),…`
- Row 7+: frame data

Skeleton exports additionally include `Bone` and `Bone Marker` column groups before the trailing `Marker` block.
