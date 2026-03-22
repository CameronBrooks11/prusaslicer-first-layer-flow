{if !is_nil(custom_parameter_filament_first_layer_extrusion_multiplier[initial_extruder])}
; FIRST_LAYER_FLOW_APPLY
M221 S{int(100 * custom_parameter_filament_first_layer_extrusion_multiplier[initial_extruder])}
{else}
; FIRST_LAYER_FLOW_APPLY
M221 S{int(100 * extrusion_multiplier[initial_extruder])}
{endif}
