Main: addi $a0, $zero, 32  # Counter for loop
      addi $a1, $zero, -1  # Value to load into memory
 L0:  addi $gp, $gp, 4     # Space for a word
      sw   $a1, 0($gp)
      addi $a0, $a0, -1    # Decrement the counter
      bgtz $a0, L0
      addi $a1, $a1, -1    # Change the word we're storing
      add  $v1, $gp, $zero # Store global pointer as return value
      jal  L1
      addi $a0, $zero, 32  # Reset counter for loop
      addi $v0, $zero, 10
      syscall

L1:   lw   $t0, 0($gp)     # Grab our first word
      addi $sp, $sp, -4    # Space on the stack for a word
      sw   $t0, 0($sp)     # Shove it back, this time on the stack
      addi $a0, $a0, -1    # Decrement the counter
      bgtz $a0, L1
      addi $gp, $gp, -4    # Move the gp
      jr   $ra

