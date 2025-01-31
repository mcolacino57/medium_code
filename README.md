# EVPI.py

- This code was produced by importing a program written in the Mathematica programming
language into Claude.ai, and prompting it to rewrite my code into Python. After a few revisions
of the prompt, and some manual debugging, a working Python program was produced.

- When this python program is run, it should produce the following output:


## Decision Analysis:

Choice: Take More Space (Vertex 2)

|Terminal | Probability | Cost ($) | Expected Value ($)|
--------------------------------------------------
      10 |      0.240 |      0.00 |             0.00
      11 |      0.120 | 700,000.00 |        84,000.00
      12 |      0.040 | 1,050,000.00 |        42,000.00
      13 |      0.200 |      0.00 |             0.00
      14 |      0.250 | 700,000.00 |       175,000.00
      15 |      0.050 | 1,050,000.00 |        52,500.00
      16 |      0.020 |      0.00 |             0.00
      17 |      0.060 | 700,000.00 |        42,000.00
      18 |      0.020 | 1,050,000.00 |        21,000.00
Total Expected Value for More Space: $416,500.00

Choice: Take No More Space (Vertex 3)

Terminal | Probability | Cost ($) | Expected Value ($)
--------------------------------------------------
      19 |      0.240 | 885,500.00 |       212,520.00
      20 |      0.120 |      0.00 |             0.00
      21 |      0.040 | 350,000.00 |        14,000.00
      22 |      0.200 | 805,000.00 |       161,000.00
      23 |      0.250 |      0.00 |             0.00
      24 |      0.050 | 350,000.00 |        17,500.00
      25 |      0.020 | 764,750.00 |        15,295.00
      26 |      0.060 |      0.00 |             0.00
      27 |      0.020 | 350,000.00 |         7,000.00
Total Expected Value for No More Space: $427,315.00

Optimal choice: Take More Space (saves $10,815.00)

## EVPI Analysis:

State-by-state comparison:
State | More Space EV | No More EV | Best EV
--------------------------------------------------
    1 | $       0.00 | $212,520.00 | $   0.00
    2 | $  84,000.00 | $     0.00 | $   0.00
    3 | $  42,000.00 | $14,000.00 | $14,000.00
    4 | $       0.00 | $161,000.00 | $   0.00
    5 | $ 175,000.00 | $     0.00 | $   0.00
    6 | $  52,500.00 | $17,500.00 | $17,500.00
    7 | $       0.00 | $15,295.00 | $   0.00
    8 | $  42,000.00 | $     0.00 | $   0.00
    9 | $  21,000.00 | $ 7,000.00 | $7,000.00

Best decision EV without perfect information: $416,500.00
Expected value with perfect information: $38,500.00
Value of perfect information: $378,000.00
