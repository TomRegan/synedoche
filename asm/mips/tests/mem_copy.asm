# Tom Regan <noreply.tom.regan@gmail.com>
# 2011-07-19
#
# @purpose: TESTING
#           copies a value from register to register via memory
# @modifies: $t0(8),
#            $t1(9),
#            $s0(16)
#            4 bytes memory on the stack

addi $t0, $zero, 255 # set t0 to 255
addi $t1, $zero, 4   # set t1 to 4
sub  $sp, $sp,   $t1 # make space for 1 word on the stack
sw   $t0, 0($sp)     # store 255 on the stack
lw   $s0, 0($sp)     # pop 255 off the stack into s0
