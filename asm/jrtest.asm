Main: jal Func               # 0x400000
      addi $s0, $zero, 255   # 0x400004
      addi $s1, $zero, 255   # 0x400008
      addi $v0, $zero, 10    # 0x40000c
      syscall                # 0x400010

Func: addi $t0, $zero, 65534 # 0x400014
      addi $t1, $zero, 65534 # 0x400018
      addi $t2, $zero, 65534 # 0x40001c
      addi $t3, $zero, 65534 # 0x400020
      addi $t4, $zero, 65534 # 0x400024
      jr   $ra               # 0x400028
      addi $t5, $zero, 65534 # 0x40002c
