Main: addi  $t0, $zero, 10
      addi  $t1, $zero, 1
Loop:
L0:   beq   $t0, $zero, Exit
L1:   sub   $t0, $t0, $t1
L2:   j     Loop
L2:   nop
Exit:
      addi  $v0, $zero, 10
      syscall
