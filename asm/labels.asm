Main: addi  $t0, $zero, 10
Loop:
      beq   $t0, $t1,   Exit
      addi  $t0, $zero, -1
      j     Loop
Exit:
