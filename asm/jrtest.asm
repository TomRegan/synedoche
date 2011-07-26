Main: jal Func
      addi $s0, $zero, 255
      addi $s1, $zero, 255
      addi $v0, $zero, 10
      syscall

Func: addi $t0, $zero, 1023
      addi $t1, $zero, 1023
      addi $t2, $zero, 1023
      addi $t3, $zero, 1023
      addi $t4, $zero, 1023
      jr   $ra
      addi $t5, $zero, 1023
