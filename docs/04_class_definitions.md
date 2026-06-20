# Class Definitions (the frozen taxonomy)

> The canonical machine-readable source is [`configs/classes.yaml`](../configs/classes.yaml).
> This document is the human-readable definition every annotator must agree on.
> **Frozen on 2026-06-20.** Changing it after annotation begins requires an ADR.

## Why these classes

Adopted from Track A's concrete scheme (the most complete of the source proposals;
see [ADR-0001](decisions/0001-scope-and-framing.md)). Detection classes are
**vehicle/agent types you can see**, plus helmet compliance and traffic signs —
*not* ownership (which needs plate colour/text and is out of scope).

## Full taxonomy — 18 classes (`profile: full`)

### Vehicles & agents (0–6)

| id | name | definition / includes | notes |
|---:|------|------------------------|-------|
| 0 | `motorcycle_scooter` | Two-wheeled motorised: motorcycle, scooter, moped. | The dominant, hardest class. Watch small/distant instances. |
| 1 | `car_van_jeep` | Private 4-wheelers: car, jeep, SUV, van, microvan. | Catch-all for ambiguous small 4-wheelers. |
| 2 | `bus_microbus` | Buses, microbuses, minibuses, coaches. | Confusable with truck; classify by passenger body. |
| 3 | `truck_tipper` | Trucks, tippers, lorries, tankers. | Confusable with bus. |
| 4 | `tempo_erickshaw` | Three-wheeled passenger/cargo: tempo, auto, e-rickshaw. | Local type absent from COCO. |
| 5 | `bicycle` | Pedal bicycles. | |
| 6 | `pedestrian` | People on foot (incl. roadside vendors standing in scene). | Not riders/passengers on a vehicle. |

### Helmet compliance (7–9)

| id | name | definition | notes |
|---:|------|-----------|-------|
| 7 | `helmet` | Head region of a rider/passenger **wearing** a helmet. | Box the head/helmet, not the whole person. |
| 8 | `no_helmet` | Head region of a rider/passenger **without** a helmet. | Only when clearly bare-headed. Don't confuse cap/hair. |
| 9 | `rider` | A person operating/seated on a two-wheeler. | Annotated separately from the vehicle and helmet box. |

### Traffic signs (10–17)

| id | name | definition |
|---:|------|-----------|
| 10 | `stop_sign` | Stop sign. |
| 11 | `no_parking` | No-parking sign. |
| 12 | `no_entry` | No-entry sign. |
| 13 | `speed_limit` | Speed-limit sign (any value). |
| 14 | `pedestrian_crossing` | Pedestrian-crossing warning sign. |
| 15 | `school_zone` | School-zone sign. |
| 16 | `traffic_light` | Signal **head** (not the pole). |
| 17 | `one_way` | One-way directional sign. |

## Reduced taxonomy — for a fast first pass (`profile: simple`)

If solo annotation volume is tight, ship vehicles first and add helmet/sign in v1.1.
The reduced profile is **3 classes**, per the source proposal's "simpler first
version":

| id | name | merges |
|---:|------|--------|
| 0 | `two_wheeler` | `motorcycle_scooter` (motorcycle + scooter merged) |
| 1 | `helmet` | head wearing a helmet |
| 2 | `no_helmet` | bare head |

> **Merge rule (frozen):** in `simple`, motorcycle and scooter are one class; in
> `full`, they remain merged into `motorcycle_scooter` (we do not attempt the
> motorcycle/scooter visual split — it is unreliable at standoff resolution).

## Optional future violation classes (not in v1)

`red_light_violation`, `wrong_lane`, `triple_riding`, `no_helmet_violation`,
`zebra_crossing_blocked`. These are behaviour/event classes for future work, not
object classes; they require tracking + rules, not just boxes.
