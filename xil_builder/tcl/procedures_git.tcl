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
