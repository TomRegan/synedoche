##########################################################################
##Author        : Tom Regan <noreply.tom.regan@gmail.com>                     ##
##Last modified : 2011-08-11                                            ##
##Description   : MIPS assembly program: finds the first number         ##
##                divisible by all numbers from 1..10                   ##
##Modifies      : registers : $s(0,1), $t0, $v(0, 1), $hi, $lo          ##
##Result        : 2520 in v1                                            ##
##########################################################################

#####################################################
##This block initializes counters and variables.   ##
#####################################################
Main:
  addi $s0, $zero, 2  # counter
  addi $s1, $zero, 10 # constant 11
  addi $v1, $zero, 10 # candidate
#####################################################
##This loop tests each number from 1..10           ##
#####################################################
L0:
  beq  $s0, $s1, Exit # if counter reaches 11, we have our number
  div  $v1, $s0       # divide to get the remainder
  mfhi $t0            # move the remainder to examine it
  bgtz $t0, Reset     # if s0 % s1 != 0, t0 is not a candidate
  nop                 #
  addi $s0, $s0, 1    # Increment s0
  j    L0             #
  nop                 #
#####################################################
##Resets counter and increment candidate.          ##
#####################################################
Reset:
  addi $s0, $zero, 2  # reset counter to 2
  add  $v1, $v1, $s1  # increment the candidate
  j    L0             # loop
#####################################################
##This block terminates the program.               ##
#####################################################
Exit:
  addi $v0, $zero, 10 # exit code
  syscall             #

#include <stdio.h>
#
#int
#main(void)
#{
#  int s1 = 21;
#  int s0 = 1;
#  int v1 = 1;
#  L0: if (s0 == s1) goto Exit;
#      if (v1 % s0 == 0) s0 = s0 + 1;
#      else goto L1;
#      goto L0;
#  L1: s0 = 1;
#      v1 = v1 + 1;
#      goto L0;
#
#  Exit: fprintf(stdout, "%i\n", j);
#  return 0;
#}
