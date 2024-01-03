proc phys_opt_loop { PRJ_NAME PRJ_DIR WNS } {
  set NLOOPS 5 
  if {$WNS < 0.000} {
    for {set i 0} {$i < $NLOOPS} {incr i} {
      phys_opt_design -directive AggressiveExplore 
      phys_opt_design -directive AggressiveFanoutOpt
      phys_opt_design -directive AlternateReplication
    }
    report_timing_summary -file $PROJ_DIR/${PROJ_NM}_post_place_physopt_tim.rpt
    report_design_analysis -logic_level_distribution \
      -of_timing_paths [get_timing_paths -max_paths 10000 \
      -slack_lesser_than 0] \ 
      -file $PROJ_DIR/post_place_physopt_vios.rpt
    write_checkpoint -force $PROJ_DIR/${PROJ_NM}_post_place_physopt.dcp
  }
}
