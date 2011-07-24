L1:
addi $t0, $zero, 255
addi $t1, $zero, 255
addi $t2, $zero, 255
j    L0
addi $t3, $zero, 255 # in delay slot, ought to be executed
addi $t4, $zero, 255 # never reached
addi $t5, $zero, 255 # never reached
L0:
addi $t6, $zero, 255
addi $t7, $zero, 255
j    L1
#nop here
