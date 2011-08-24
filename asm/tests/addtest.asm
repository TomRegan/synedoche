addi $a0, $zero, -1
addi $a1, $zero, -1
add  $s0, $a0, $a1
addi $a2, $zero, 1
addi $a3, $zero, 1
add  $s1, $a2, $a3
addi $s2, $a0, -1   # Same as line 3
addi $s3, $a2, 1    # Same as line 6
addi $v0, $zero, 10
syscall
