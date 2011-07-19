#Tom Regan <thomas.c.regan@gmail.com>
#2011-07-04
#add.asm-- Computes the sum of 1 and 2
#modifies: t0 (result)
#          t1 (operand)
main:    addi  $t0, $zero, 2  #t0 <- 2
         addi  $t1, $zero, 2  #t1 <- 2
         add   $t0, $t0,  $t1 #t0 <- 2 + 2
         addi  $v0, $zero, 10 #syscall code for exit
         slt   $v0, $t0,  $t1 #v0=1 iff t0<t1 else v0=0
#end
