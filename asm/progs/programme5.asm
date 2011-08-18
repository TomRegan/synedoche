Main:
  addi $a0, $zero, 5
  addi $v1, $zero, 1
  jal  Fact
  addi $v0, $zero, 10
  syscall
Fact:
  beq  $a0, $zero, Exit
  mult $a0, $v1
  mflo $v1
  j  Fact
  addi $a0, $a0, -1
Exit:
  jr $ra
