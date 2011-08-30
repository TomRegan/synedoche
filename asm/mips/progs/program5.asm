##########################################################################
##Author        : Tom Regan <code.tregan@gmail.com>                     ##
##Last modified : 2011-07-22                                            ##
##Description   : MIPS assembly program: Calculates factorial           ##
##                tail-recursively                                      ##
##Modifies      : registers : $a0, $v(0, 1), $hi, $lo, $ra              ##
##Result        : 120 in v1                                             ##
##########################################################################

#####################################################
##This block is the equivalent of a main function. ##
#####################################################
Main:
  addi $a0, $zero, 5    # target (counter)
  addi $v1, $zero, 1    #
  jal  Fact             # call the function
  addi $v0, $zero, 10   # exit call (delay slot)
  syscall               #
#####################################################
##This block is a factorial function.              ##
#####################################################
Fact:
  beq  $a0, $zero, Exit # don't do any work if a0 is 0
  mult $a0, $v1         #
  mflo $v1              # store the result in v1
  j  Fact               #
  addi $a0, $a0, -1     # decrement a0
Exit:                   #
  jr $ra                #
