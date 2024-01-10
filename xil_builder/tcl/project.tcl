#######################################
# create project
#######################################
if { ![file exists ${PRJ_DIR}/${PRJ_NAME}.xpr] } {
  create_project $PRJ_NAME $PRJ_DIR -part $PART -force
  set_property XPM_LIBRARIES {XPM_CDC XPM_MEMORY XPM_FIFO} [current_project]
  set_property target_language VHDL [current_project]
} else {
  open_project ${PRJ_DIR}/${PRJ_NAME}.xpr
}