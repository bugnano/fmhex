110 INPUT "Input archive - ", inf$
120 INPUT "output archve - ", outf$
130 OPEN inf$ FOR INPUT AS #1
140 OPEN outf$ FOR RANDOM AS #2 LEN=1
150 FIELD #2, 1 AS s$
160 WHILE NOT EOF(1)
170   INPUT #1, l$
180   IF LEFT$(l$, 1) <> ":" THEN 290
190   c = 2
200   WHILE c < LEN(l$)
210     a = ASC(MID$(l$, c, 1)) - 48
220     IF a > 9 THEN a = a - 7
230     b = ASC(MID$(l$, c + 1, 1)) - 48
240     IF b > 9 THEN b = b - 7
250     LSET s$=CHR$(a * 16 + b)
260     PUT #2
270     c = c + 2
280   WEND
290 WEND
300 CLOSE #1
310 CLOSE #2
