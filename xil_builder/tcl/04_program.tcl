open_hw_manager
connect_hw_server -url localhost:3121
current_hw_device [ get_hw_targets */xilinx_tcf/Digilent/* ]
open_hw_target
current_hw_device [lindex [get_hw_devices] 0]
refresh_hw_device -update_hw_probes false [lindex [get_hw_devices] 0]

set bitfile "./deploy/latest-zybo.bit"
set ltxfile "./deploy/latest-zybo.ltx"

puts $bitfile
puts $ltxfile

if { [file exists $bitfile] } {
  set_property PROGRAM.FILE [file normalize $bitfile ] [lindex [get_hw_devices] 1]
} else {
  puts "WARN: NO PROGRAMMING FILE"
}

if { [file exists $ltxfile] } {
  set_property PROBES.FILE  [file normalize $ltxfile ] [lindex [get_hw_devices] 1]
} else {
  puts "WARN: NO DEBUGGING FILE"
}
program_hw_devices [lindex [get_hw_devices] 1]
refresh_hw_device [lindex [get_hw_devices] 1]

