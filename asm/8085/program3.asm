;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;Author        : Tom Regan <code.tregan@gmail.com>                     ;;
;;Last modified : 2011-08-30                                            ;;
;;Description   : 8085 assembly program: computes an 8-bit factorial.   ;;
;;Modifies      : registers : A, B, C, D, H, L                          ;;
;;Result        : 120                                                   ;;
;;Notes         : This version is going to run on a test simulator      ;;
;;                and contails NOPs for the purpose of mitigating       ;;
;;                branch delay cycles. Don't remove these while         ;;
;;                running on Sunray.                                    ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;This block initializes counters and variables.   ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
start: NOP
  ADI 5     ; The number to compute (Loaded in ACC).
  CPI 2     ; If computation is less than 1, end.
  JC end
  NOP       ; This implementation is going to run PP.
  MVI D, 0
  MOV E, A
  DCR A     ; Get the next number down in A...
  MOV C, A  ; ...and load it into C.
  CALL fact
  NOP
  JMP end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;Recursively calculates the factorial.            ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
fact: NOP
  MOV B, C  ; Load the counter.
l0: NOP
  DAD D     ; (Stores the result in H/L)
  DCR B
  JNZ l0    ; Multiply by a series of additions.
  NOP
  MOV E, L  ; Store the intermediary result.
  MVI L, 0H
  DCR C     ; Decrement the counter.
  CNZ fact  ; Call factorial again.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;Terminates the program.                          ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
end: NOP
  HLT
