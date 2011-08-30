Main: addi $v0, $v0, 5
      beq  $v0, $t0, Exit
      addi $t0, $zero, 10
      add  $t1, $zero, $t0
      beq  $t0,  $t1, Main
      nop
Exit: syscall
