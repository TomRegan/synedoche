      addi $s0, $zero, 10
Main: addi $v0, $v0, 1
      nop
      nop
      nop
      bne  $v0, $s0, Main
      nop
      syscall
