# Author        : Tom Regan <thomas.c.regan@gmail.com>
# Last modified : 2011-08-16
# Description   : Does an O(n^2) sort on an unsorted list.
# Modifies      : registers : $t(0..9)
#                 memory    : Stack(40b)

Main: addi $a0, $zero, 10  # loop counter
      add  $t0, $zero, $a0 # store value
L0:   addi $sp, $sp,   -4  ##
      sw   $a0, 0($sp)     # load loop
      bgtz $a0, L0         ##
      addi $a0, $a0,   -1  # decrement counter (delay slot)
      jal  Sort
      addi $a0, $zero, 10  # reset counter (delay slot)
      # return
      addi $v0, $zero, 10
      syscall

Sort: add  $fp, $zero, $sp # use fp to store and retrieve
      addi $a1, $zero, 9   # a1 will be inner loop counter
      bgtz $a0, L1
      nop
      jr   $ra

L1:   lw   $s0, 0($fp)     # load and examine two values
      lw   $s1, 4($fp)
      slt  $s2, $s1, $s0
      bgtz $s2, L1         # if s0 > s1 goto L1
      addi $a1, $a1, -1    # decrement inner loop counter
      sw   $s0, 4($fp)     # swap
      sw   $s1, 0($fp)
      bgtz $a1, L1         # while a0 > 0 goto L1
      addi $fp, $zero, -4
      jr   $ra
