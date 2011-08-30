##########################################################################
##Author        : Tom Regan <code.tregan@gmail.com>                     ##
##Last modified : 2011-07-21                                            ##
##Description   : MIPS assembly program: finds the sum of all numbers   ##
##                below 1000 that are multiples of 3 or 5               ##
##Modifies      : registers : $s(0,1,2,3,4), $t0, LO, HI                ##
##                memory    : none                                      ##
##Result        : 233168                                                ##
##########################################################################

#####################################################
##This block initializes counters and variables.   ##
#####################################################
Main:
  addi $s0, $zero, 0    # counter
  addi $s1, $zero, 0    # sum (0)
  addi $s2, $zero, 1000 # end (1000)
  addi $s3, $zero, 3    # constant 3
  addi $s4, $zero, 5    # constant 5

#####################################################
##This loop calculates the remainder of candidates.##
#####################################################
L0:
  addi $s0, $s0, 1      # increment variable s0
  beq  $s0, $s2, Exit   # if s0 = 1000, Exit
  div  $s0, $s3         # s0<-s0/3 (result in HI)
  mfhi $t0              # t0<-HI (remainder)
  beq  $t0, $zero, L1   # goto L1 if rem = 0
                        # there is _no_ dependency on t0
  div  $s0, $s4         # s0<-s0/5 (result in HI)
  mfhi $t0              # t0<-HI (remainder)
  beq  $t0, $zero, L1   # goto L1 if rem = 0
  nop                   # fill delay slot
  j    L0               # continue loop
  nop                   # branch delay slot

#####################################################
##Short loop to increment the sum.                 ##
#####################################################
L1:
  add  $s1, $s1, $s0    # increment the total
  j    L0               # loop

#####################################################
##This block terminates the program.               ##
#####################################################
Exit:
  add  $v1, $zero, $s1  # return value in s1
  addi $v0, $zero, 10   # exit code
  syscall

#include <stdio.h>
#
#int
#main(void)
#{
#  int i = 0;
#  int sum = 0;
#
#  L0: if(i == 1000) goto Exit;
#      if (i % 3 == 0 || i % 5 ==0) sum = sum + i;
#      i = i + 1;
#      goto L0;
#
#  Exit: fprintf(stdout, "%i\n", sum);
#  return 0;
#}
#
