##############################################
# Start synthesis (conditional)
##############################################
if {$ena_syn || $ena_impl } {
  reset_runs synth_1
  catch { launch_runs synth_1 -jobs 24 }
  catch { wait_on_runs synth_1 }
  set syn_prog [get_property PROGRESS [get_run synth_1]]
  set syn_stat [get_property STATUS [get_run synth_1]]
  puts $syn_prog
  puts $syn_stat

  if {$syn_prog ne "100%" || ![string match "*synth_design Complete!*" $syn_stat]} {
    exit 2
  }
}

##############################################
# Start implementation (conditional)
##############################################
if { $ena_impl } {
  launch_runs impl_1 -to_step write_bitstream -jobs 24
  catch { wait_on_run impl_1 }
  set imp_prog [get_property PROGRESS [get_run impl_1]]
  set imp_stat [get_property STATUS [get_run impl_1]]
  puts $imp_prog
  puts $imp_stat
  if {$imp_prog ne "100%"} {
    exit 3
  }

} else {
  puts "Skipping implementation"
  exit 0
}

##############################################
# start post build
##############################################
open_run impl_1
set BUILD_DATE    [ clock format [ clock seconds ] -format %Y-%m-%d ]
set BUILD_TIME    [ clock format [ clock seconds ] -format %H-%M-%S ]
set BUILD_REV     [ git_revision ]
set BUILD_BRANCH  [ git_branch   ]

set WNS "0.00"
catch {set WNS [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]}
puts "Post Route WNS = $WNS"

file mkdir $PRJ_DIR/deploy
write_debug_probes -force $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.ltx
write_bitstream    -force $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.bit -bin_file
write_hw_platform  -file  $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.xsa -force -fixed -include_bit
archive_project           $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.zip

catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.xsa" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.xsa"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.bit" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.bit"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.bin" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.bin"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.ltx" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.ltx"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.zip" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.zip"}