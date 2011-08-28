# Author        : Tom Regan <code.tregan@gmail.com>
# Last modified : 2011-07-22
# Description   : MIPS assembly program: Calculates factorial recursively
#                 Calculates !10, stores result in $v0
# Modifies      : registers : $s(0,1,2,3,4), $a0, LO, HI, $ra
#                 memory    : Stack
Main:
  addi $a0, $zero, 5    # factorial
  jal  Fact             # call factorial procedure
  addi $s1, $zero, 1    # global constant 1 (delay slot)
  j    Exit
  add  $v1, $zero, $v0  # save result in v0 (delay slot)
# Factorial sum
Fact:
  slti $v0, $a0, 1      # v0<-1 if n = 0 ...
  beq  $v0, $zero, F0   # if n>0 goto F0 (effectively, recurse)
  nop
  jr   $ra              # else return (to end via Main)
  nop
# Function call
F0: 
  addi $sp, $sp, -12    # space for three registers on stack
  sw   $sp, 8($sp)      # store the stack pointer
  sw   $a0, 4($sp)      # store the argument
  sw   $ra, 0($sp)      # store the return address
  sub  $a0, $a0, $s1    # n = n - 1
  jal  Fact             # call fact with n
  nop                   # delay slot... yawn
  addi $sp, $sp, 12     # BUG FIX!
  lw   $ra, 0($sp)      # pop return address
  lw   $a0, 4($sp)      # pop arg0
  lw   $sp, 8($sp)      # pop stack pointer
  mult $v0, $a0         # n<-n*(n-1)
  mflo $v0
  jr   $ra
  nop
Exit:
  addi $v0, $zero, 10   # exit code
  syscall

#include <stdio.h>
#
#int
#factorial (int n)
#{
#  if (n == 0) return 1;
#  return n * factorial(n-1);
#}
#
#int
#main(void)
#{
#  int a = 10;
#  int b;
#
#  b = factorial(a);
#
#  fprintf(stdout, "%i\n", b);
#
#  return 0;
#}
