##########################################################################
##Author        : Tom Regan <noreply.tom.regan@gmail.com>                     ##
##Last modified : 2011-07-21                                            ##
##Description   : MIPS assembly program: Calculates factorial           ##
##                iteratively                                           ##
##Modifies      : registers : $s(0,1), $v(0, 1), $hi, $lo               ##
##Result        : 120 in v1                                             ##
##########################################################################

#####################################################
##This block initializes counters and variables.   ##
#####################################################
Main:
  addi $s0, $zero, 5    # factorial
  addi $v1, $zero, 1    # sum
  addi $s1, $zero, 1    # constant 1
#####################################################
##This block iterates over 5..0 to compute fact.   ##
#####################################################
L0:
  beq  $s0, $zero, Exit # terminate on zero
  mult $s0, $v1         #
  sub  $s0, $s0, $s1    # decrement factorial
  mflo $v1              # move result into sum
  j    L0               #
  nop                   #
#####################################################
##This block terminates the program.               ##
#####################################################
Exit:
  addi $v0, $zero, 10   # exit code
  syscall               #

#include <stdio.h>
#
#int
#main(void)
#{
#  int a=10;
#  int b=1;
#
#  L0: if (a == 0) goto Exit;
#  b = b * a;
#  a = a - 1;
#  goto L0;
#  Exit: fprintf(stdout, "%i\n", b);
#  return 0;
#}
