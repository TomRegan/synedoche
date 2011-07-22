Main: addi  $t0, $zero, 10
      addi  $t1, $zero, 1
Loop:
      beq   $t0, $zero, Exit
      sub   $t0, $t0, $t1
      j     Loop
Exit:
