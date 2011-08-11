Main: addi $a0, $zero, 10
      addi $v1, $zero, 1
Fact: beq  $a0, $zero, Exit
      mult $a0, $v1
      mflo $v1
      addi $a0, $a0, -1
      j Fact
      nop
Exit: addi $v0, $zero, 10
      syscall
