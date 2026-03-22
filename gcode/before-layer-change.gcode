{if layer_num == 1}
; FIRST_LAYER_FLOW_RESET
M221 S{int(100 * extrusion_multiplier[current_extruder])}
{endif}
