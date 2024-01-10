##############################################
# Start synthesis (conditional)
##############################################
if {$ena_syn || $ena_impl } {
  reset_runs synth_1
  catch { launch_runs synth_1 -jobs 24 -scripts_only }
  catch { launch_runs synth_1 -jobs 24 }
  wait_on_run synth_1
}

##############################################
# Start implementation (conditional)
##############################################
if {$ena_syn || $ena_impl } {
  launch_runs impl_1 -to_step write_bitstream -jobs 24
  wait_on_run impl_1
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

file mkdir -p $PRJ_DIR/deploy
write_debug_probes -force $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.ltx
write_bitstream    -force $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.bit -bin_file
write_hw_platform  -file  $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.xsa -force -fixed -include_bit
archive_project           $PRJ_DIR/deploy/${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.zip

catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.xsa" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.xsa"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.bit" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.bit"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.bin" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.bin"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.ltx" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.ltx"}
catch {exec ln -sf "${PRJ_NAME}_${BUILD_BRANCH}_${BUILD_REV}_${BUILD_DATE}_${BUILD_TIME}_${WNS}ns.zip" "$PRJ_DIR/deploy/latest-${PRJ_NAME}.zip"}