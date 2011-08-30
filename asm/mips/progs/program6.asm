##########################################################################
##Author        : Tom Regan <code.tregan@gmail.com>                     ##
##Last modified : 2011-07-22                                            ##
##Description   : MIPS assembly program: Copies a portion of memory     ##
##                from data to stack                                    ##
##Modifies      : registers : $a(0, 1) $v(0, 1), $t0, $sp, $gp, $ra     ##
##Result        : data copied from sp to gp location                    ##
##########################################################################

#####################################################
##This block initializes counters and variables.   ##
#####################################################
Main:
  addi $a0, $zero, 32  # Counter for loop
  addi $a1, $zero, -1  # Value to load into memory
#####################################################
##This block loads data into the data segment.     ##
#####################################################
L0:
  addi $gp, $gp, 4     # Space for a word
  sw   $a1, 0($gp)     #
  addi $a0, $a0, -1    # Decrement the counter
  bgtz $a0, L0         #
  addi $a1, $a1, -1    # Change the word we're storing
  add  $v1, $gp, $zero # Store global pointer as return value
  jal  L1              #
  addi $a0, $zero, 32  # Reset counter for loop
  addi $v0, $zero, 10  #
  syscall              #
#####################################################
##This loop copies data to the stack.              ##
#####################################################
L1:
  lw   $t0, 0($gp)     # Grab our first word
  addi $sp, $sp, -4    # Space on the stack for a word
  sw   $t0, 0($sp)     # Shove it back, this time on the stack
  addi $a0, $a0, -1    # Decrement the counter
  bgtz $a0, L1         #
  addi $gp, $gp, -4    # Move the gp
  jr   $ra             #
