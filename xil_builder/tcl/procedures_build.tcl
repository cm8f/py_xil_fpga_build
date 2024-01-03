set BUILD_DATE    [ clock format [ clock seconds ] -format %Y%d%m ]
set BUILD_TIME    [ clock format [ clock seconds ] -format %H%M%S ] 
set BUILD_REV     [ git_revision ] 
set BUILD_BRANCH  [ git_branch   ] 
set archive       1


####################################
# Constraints
####################################
set constrs [glob ../xdc/*.xdc]
foreach c $constrs {
  puts "add XDC $c"
  read_xdc $c
}


####################################
# IPs
####################################
#set ips [glob ../hdl/ip/*/*.xci]
#foreach i $ips {
#  puts "add IP $i"
#  read_ip $i
#}
#upgrade_ip [get_ips *]
#generate_target all [get_ips *]


####################################
# sources
####################################
set vhd   [ glob ../hdl/*.vhd ]
foreach f $vhd {
  puts "READ VHDL FILE: $f"
  read_vhdl -vhdl2008 $f
}
set vhd   [ glob ../hdl/trigger/*.vhd ]
foreach f $vhd {
  puts "READ VHDL FILE: $f"
  read_vhdl -vhdl2008 $f
}
#set vlog  [ glob ../hdl/*.v ] 
#foreach f $vlog {
#  puts "READ VERILOG FILE: $f"
#  read_verilog $f
#}

set submodules [ glob -type d -path ../hdl/submodules/ * ]
foreach s $submodules {
  set submodule_files [ glob $s/hdl/*.vhd ] 
  set lib [file tail $s]
  foreach f $submodule_files {
    puts "add LIB=$lib: $f"
    read_vhdl -vhdl2008 -library $lib $f
  }
}


####################################
# Build board design
####################################
set_part $PART_NAME
set bds [glob ../hdl/bd/*.tcl]
foreach b $bds {
  puts "found BD: $b"
  set bdname [file rootname [file tail $b]]
  source $b
  make_wrapper -files [get_files .srcs/sources_1/bd/${bdname}/${bdname}.bd] -top -inst_template -testbench
  catch { add_files -norecurse .gen/sources_1/bd/${bdname}/hdl/${bdname}_wrapper.v } 
  catch { add_files -norecurse .gen/sources_1/bd/${bdname}/hdl/${bdname}_wrapper.vhd } 
  generate_target all [get_files .srcs/sources_1/bd/${bdname}/${bdname}.bd]
}

set export2deploy 0



####################################
# only sythesize
####################################
if { $STRATEGY == "synOnly" } {
  synth     $PRJ_NAME $PRJ_DIR $DEFINES $SYNTH_ARGS $TOP_MODULE $PART_NAME 
  opt       $PRJ_NAME $PRJ_DIR 

} elseif { $STRATEGY == "placeExplore" } {
  if { ![file exists $PRJ_DIR/PRJ_NAME_post_opt.dcp] } {
    synth     $PRJ_NAME $PRJ_DIR $DEFINES $SYNTH_ARGS $TOP_MODULE $PART_NAME 
    opt       $PRJ_NAME $PRJ_DIR 
  }
  place_directive_explore $PRJ_NAME $PRJ_DIR
     
} elseif { $STRATEGY == "fitOnce"} {
  synth     $PRJ_NAME $PRJ_DIR $DEFINES $SYNTH_ARGS $TOP_MODULE $PART_NAME 
  opt       $PRJ_NAME $PRJ_DIR 
  place     $PRJ_NAME $PRJ_DIR 
  phys_opt  $PRJ_NAME $PRJ_DIR 
  set wns [route     $PRJ_NAME $PRJ_DIR ]
  bitfile   $PRJ_NAME $PRJ_DIR $BUILD_DATE $BUILD_TIME $wns $BUILD_BRANCH $BUILD_REV
  set export2deploy 1

} elseif { $STRATEGY == "physOptLoop" } {
  synth     $PRJ_NAME $PRJ_DIR $DEFINES $SYNTH_ARGS $TOP_MODULE $PART_NAME 
  opt       $PRJ_NAME $PRJ_DIR 
  place     $PRJ_NAME $PRJ_DIR 
  set WNS [ get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup] ]
  phys_opt_loop $PRJ_NAME $PRJ_DIR $WNS 
  set wns [route     $PRJ_NAME $PRJ_DIR ]
  bitfile   $PRJ_NAME $PRJ_DIR $BUILD_DATE $BUILD_TIME $wns $BUILD_BRANCH $BUILD_REV
  set export2deploy 1
} else {
  puts "unknown strategy $STRATEGY"
}

# ARCHIVE 
if { $archive } {
  save_project_as $PRJ_NAME ../workspace/${PRJ_NAME} -force
  archive_project "../deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.zip"
  close_project
  exec ln -sf     "../deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.zip"  "../deploy/latest-${PRJ_NAME}.zip"
}

if { $export2deploy } {
  read_checkpoint ../workspace/${PRJ_NAME}/${PRJ_NAME}_post_route.dcp
  open_checkpoint ../workspace/${PRJ_NAME}/${PRJ_NAME}_post_route.dcp
  write_hw_platform -fixed -include_bit -force -file  ../deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}.xsa 

  file rename         [file normalize ../workspace/$PRJ_NAME/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.bit] ../deploy/
  file rename         [file normalize ../workspace/$PRJ_NAME/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.bin] ../deploy/
  catch {file rename  [file normalize ../workspace/$PRJ_NAME/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.ltx] ../deploy/}

  exec ln -sf         "../deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}.xsa"           "../deploy/latest-${PRJ_NAME}.xsa"
  exec ln -sf         "../deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.bit"  "../deploy/latest-${PRJ_NAME}.bit"
  exec ln -sf         "../deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.bin"  "../deploy/latest-${PRJ_NAME}.bin"
  catch {exec ln -sf  "../deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${wns}ns.ltx"  "../deploy/latest-${PRJ_NAME}.ltx"}

  # REPORTS:
  set rpts [glob ../workspace/$PRJ_NAME/*.rpt]
  # TODO


}
