# Author        : Tom Regan <thomas.c.regan@gmail.com>
# Last modified : 2011-07-21
# Description   : MIPS assembly program: Calculates factorial iteratively

Main:
    addi $s0, $zero, 5    # factorial
    addi $v1, $zero, 1    # sum
    addi $s2, $zero, 1    # constant 1
L0: beq  $s0, $zero, Exit # terminate on zero
    mult $s0, $v1
    sub  $s0, $s0, $s2    # decrement factorial
    mflo $v1              # move result into sum
    j    L0
    nop
Exit:
    addi $v0, $zero, 10   # exit code
    syscall

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
