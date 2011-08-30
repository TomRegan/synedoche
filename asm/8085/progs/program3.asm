;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;Author        : Tom Regan <code.tregan@gmail.com>                     ;;
;;Last modified : 2011-08-30                                            ;;
;;Description   : 8085 assembly program: computes an 8-bit factorial.   ;;
;;Modifies      : registers : A, B, C, D, H, L                          ;;
;;Result        : 120                                                   ;;
;;Notes         : This version is going to run on a test simulator      ;;
;;                and contains NOPs for the purpose of mitigating       ;;
;;                branch delay cycles.                                  ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;This block initializes counters and variables.   ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
start: NOP
  ADI 5     ; The number to compute (Loaded in A).
  CPI 2     ; If computation is less than 1, end.
  JC end
  NOP
  MOV E, A
  DCR A     ; Get the next number down in A...
  MOV C, A  ; ...and load it into C.
  MVI A, 0  ; Clear A for calculations.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;Recursively calculates the factorial.            ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
fact: NOP
  MOV B, C  ; Load the counter.
l0: NOP     ; Multiplication loop.
  ADD E     ; It's not like I'm asking for floats.
  DCR B     ; 250 useless instructions and no MUL.
  JNZ l0    ; Multiply by a series of additions.
  NOP
  MOV E, A  ; Store the intermediary result.
  MVI A, 0
  DCR C     ; Decrement the counter.
  JNZ fact  ; Call factorial again.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;Terminates the program.                          ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
end: NOP
  MOV A, E  ; Store return value in A (should be on stack)
  HLT
