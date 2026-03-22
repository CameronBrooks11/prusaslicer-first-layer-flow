; START
; FIRST_LAYER_FLOW_APPLY
M221 S102
G28
G1 X10 Y10 Z0.2 F1800
; only one layer in this file, no layer-change reset section emitted
G1 X20 Y20 E1.2
