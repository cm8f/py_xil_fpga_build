proc git_revision { } {
  # The Maximum number of seconds
  set cmd "git rev-parse --short=5 HEAD"
  if {[catch {open "|$cmd"} input] } {
    return -code error $input
  } else {
    gets $input line
    set git_hash $line
    close $input
  }
  return $git_hash
}

proc git_branch { } {
  # The Maximum number of seconds
  set cmd "git branch --show-current"
  if {[catch {open "|$cmd"} input] } {
    return -code error $input
  } else {
    gets $input line
    set git_hash $line
    close $input
  }
  return $git_hash
}

proc synth {PRJ_NAME PRJ_DIR SYNTH_ARGS TOP_MODULE PART} {
  eval "synth_design $SYNTH_ARGS -top $TOP_MODULE -part $PART"
  report_timing_summary -file $PRJ_DIR/${PRJ_NAME}_post_synth_tim.rpt
  report_utilization -file $PRJ_DIR/${PRJ_NAME}_post_synth_util.rpt
  write_checkpoint -force $PRJ_DIR/${PRJ_NAME}_post_synth.dcp
}

proc opt {PRJ_NAME PRJ_DIR {DIRECTIVE "Explore"}} {
  opt_design -directive $DIRECTIVE
  report_timing_summary -file $PRJ_DIR/${PRJ_NAME}_post_opt_tim.rpt
  report_utilization -file $PRJ_DIR/${PRJ_NAME}_post_opt_util.rpt
  write_checkpoint -force $PRJ_DIR/${PRJ_NAME}_post_opt.dcp
  set_property SEVERITY {ERROR} [get_drc_checks DSPS-*]
  report_drc -file $PRJ_DIR/${PRJ_NAME}_post_opt_drc.rpt
}

proc place {PRJ_NAME PRJ_DIR {DIRECTIVE "Explore"} } {
  place_design -directive $DIRECTIVE 
  report_timing_summary -file $PRJ_DIR/${PRJ_NAME}_post_place_tim.rpt
  report_utilization -file $PRJ_DIR/${PRJ_NAME}_post_place_util.rpt
  write_checkpoint -force $PRJ_DIR/${PRJ_NAME}_post_place.dcp
}

proc phys_opt {PRJ_NAME PRJ_DIR {DIRECTIVE "AggresiveExplore"}} {
  phys_opt_design -directive $DIRECTIVE
  report_timing_summary -file $PRJ_DIR/${PRJ_NAME}_post_place_physopt_tim.rpt
  report_utilization -file $PRJ_DIR/${PRJ_NAME}_post_place_physopt_util.rpt
  write_checkpoint -force $PRJ_DIR/${PRJ_NAME}_post_place_physopt.dcp
}

proc route {PRJ_NAME PRJ_DIR {$DIRECTIVE "Explore"}} {
  route_design -directive $DIRECTIVE
  report_timing_summary -file $PRJ_DIR/${PRJ_NAME}_post_route_tim.rpt
  report_utilization -hierarchical -file $PRJ_DIR/${PRJ_NAME}_post_route_util.rpt
  report_route_status -file $PRJ_DIR/${PRJ_NAME}_post_route_status.rpt
  report_io -file $PRJ_DIR/${PRJ_NAME}_post_route_io.rpt
  report_power -file $PRJ_DIR/${PRJ_NAME}_post_route_power.rpt
  report_design_analysis -logic_level_distribution \
   -of_timing_paths [get_timing_paths -max_paths 10000 \
   -slack_lesser_than 0] \
   -file $PRJ_DIR/${PRJ_NAME}_post_route_vios.rpt
  write_checkpoint -force $PRJ_DIR/${PRJ_NAME}_post_route.dcp

  set WNS "0.00"
  catch {set WNS [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]}
  puts "Post Route WNS = $WNS"
  return $WNS
}

proc bitfile {PRJ_NAME PRJ_DIR BUILD_DATE BUILD_TIME WNS BUILD_BRANCH BUILD_REV } {
  write_debug_probes -force $PRJ_DIR/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.ltx
  write_bitstream    -force $PRJ_DIR/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.bit -bin_file
}

proc syn_only {NAME DIR ARGS TOP PART} {
  synth     $NAME $DIR $ARGS $TOP $PART
  opt       $NAME $DIR 
}

proc fit_once {NAME DIR ARGS TOP PART} {
  synth     $NAME $DIR $ARGS $TOP $PART
  opt       $NAME $DIR 
  place     $NAME $DIR 
  phys_opt  $NAME $DIR 
  set wns [route     $NAME $DIR ]
  set BUILD_DATE    [ clock format [ clock seconds ] -format %Y%d%m ]
  set BUILD_TIME    [ clock format [ clock seconds ] -format %H%M%S ] 
  set BUILD_REV     [ git_revision ] 
  set BUILD_BRANCH  [ git_branch   ] 

  bitfile   $NAME $DIR $BUILD_DATE $BUILD_TIME $wns $BUILD_BRANCH $BUILD_REV
  write_hw_platform -fixed -include_bit -force -file  ${DIR}/${NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}.xsa 
}
