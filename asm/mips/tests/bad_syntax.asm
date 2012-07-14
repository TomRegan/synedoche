# Author        : Tom Regan <noreply.tom.regan@gmail.com>
# Last modified : 2011-08-12
# Description   : Does an O(n^2) sort on an unsorted list.
# Modifies      : registers : $t(0..9)
#                 memory    : Stack(40b)

Main:  addi $t0, $zero, 7   # Store some values to be sorted
       addi $t1, $zero, 5
       addi $t2, $zero, 2
       addi $t3, $zero, 8
       addi $t4, $zero, 4
       addi $t5, $zero, 9
       addi $t6, $zero, 0
       addi $t7, $zero, 1
       addi $t8, $zero, 6
       addi $t9, $zero, 3
       addi $s0, $zero, 10  # Outer loop counter for the sort
       jal  Stack
       addi $v0, $zero, 10
       syscall
Stack: addi $sp, $sp,  -40
       sw   $t0,  0($sp)
       sw   $t1,  4($sp)
       sw   $t2,  8($sp)
       sw   $t3, 12($sp)
       sw   $t4, 16($sp)
       sw   $t5, 20($sp)
       sw   $t6, 24($sp)
       sw   $t7, 28($sp)
       sw   $t8, 32($sp)
       sw   $t9, 36($sp)
Sort:  add  $fp, $zero, $sp # Set the fp to the current sp
       addi $s1, $zero, 10  # Inner loop counter for the sort
# Todo: Discovered a bug in the system here. No comma after rs led to
#       crash in linker with nul object. More strict checking needed?
#       Possibly reject based on regex?
       bgtz $s0  Loop       # Continue if s0 > 0
       addi $s0, $s0, -1    # This is executed each time
       jr   $ra
       nop
Loop:  addi $s1, $s1,  -2   # Decrement inner loop counter
       beq  $s1, $s5,   Sort
       lw   $s2, 0($fp)
       lw   $s3, 4($fp)
       slt  $s4, $s2,   $s3
       beq  $s4, $zero, Swap
       nop
       addi $fp, $fp,   4
       j    Loop
Swap:  add  $s4, $zero, $s2 # This is the temp value for a swap
       add  $s2, $zero, $s3
       add  $s3, $zero, $s4
       sw   $s2, 0($fp)
       sw   $s3, 4($fp)
       addi $s1, $s1,  -2
       j    Loop
       addi $fp, $fp,   4
