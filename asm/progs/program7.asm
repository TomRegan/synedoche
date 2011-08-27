# Author        : Tom Regan <thomas.c.regan@gmail.com>
# Last modified : 2011-08-16
# Description   : Does an O(n^2) sort on an unsorted list.
# Modifies      : registers : $t(0..9)
#                 memory    : Heap at gp (40b in place)

Main:
  addi $s0, $zero, 10   # loop counter
  addi $sp, $sp,   -4
  sw   $gp, 0($sp)      # save the global pointer
L0:   # load loop
  sw   $s0, 0($gp)
  addi $gp, $gp,   4
  bgtz $s0, L0
  addi $s0, $s0,   -1   # decrement counter (delay slot)
  addi $s0, $zero, 10   # reset counter
L1:
  addi $s1, $zero, 9    # inner loop counter for sort
  addi $s0, $s0,   -1   # decrement counter
  lw   $gp, 0($sp)      # load original gp value
  addi $gp, $gp,   -4   # FIX: fencepost error
L2:   # sort loop
  beq  $s0, $zero, Exit
  addi $gp, $gp,   4    # increment the gp
  beq  $s1, $zero, L1
  addi $s1, $s1,   -1   # decrement inner loop counter (delay slot)
  lw   $a0, 0($gp)
  lw   $a1, 4($gp)
  slt  $t2, $a1,   $a0  # we will sort so t0 is smaller than t1
  beq  $t2, $zero, L2   # if t0 > t1 goto L2
  nop
  addi $sp, $sp,   -4   # else swap
  jal  Swap
  sw   $ra, 0($sp)
  sw   $v0, 0($gp)
  sw   $v1, 4($gp)
  lw   $ra, 0($sp)      # restore saved values
  addi $sp, $sp,   4
  j    L2
  nop


Swap:
  add  $v0, $zero, $a1
  jr   $ra
  add  $v1, $zero, $a0


Exit:
  addi $v0, $zero, 10
  syscall
