#######################################
# Git Procedures
#######################################
proc git_revision { } {
  # The Maximum number of seconds
  #set cmd "git rev-parse --short=8 HEAD"
  set cmd "git describe --always --dirty"
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
  set git_hash [string map {"/" "-"} $git_hash]
  return $git_hash
}