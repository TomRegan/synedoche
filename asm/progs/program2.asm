# Author        : Tom Regan <thomas.c.regan@gmail.com>
# Last modified : 2011-08-11
# Description   : MIPS assembly program: finds the first number
#                 divisible by all numbers from 1..10
# Result        : Programme will exit with 2520 in v1
# TODO : Format cleanly. 2011-08-18

Main:
    addi $s0, $zero, 2  # counter
    addi $s1, $zero, 10 # constant 11
    addi $v1, $zero, 10 # candidate
L0: beq  $s0, $s1, Exit # if counter reaches 11, we have our number
    div  $v1, $s0
    mfhi $t0
    bgtz $t0, L1        # t0 is not a candidate
    nop
    addi $s0, $s0, 1    # Increment s0
    j    L0
    nop

# snippet to reset counter and increment candidate
L1: addi $s0, $zero, 2  # reset counter to 2
    add  $v1, $v1, $s1  # increment the candidate
    j    L0             # loop

Exit:
    addi $v0, $zero, 10 # exit code
    syscall

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
