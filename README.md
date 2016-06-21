# fp-growth
A command line executable python implementation for frequent item set mining. 

## Code Example
command:

    $ python FpGrowth.py retail_25k.dat 4
    
output:


    Done collecting transaction. 25000 transactions and 11427 unique items
    1 - 7232
    2 - 54715
    3 - 76151
    4 - 56225
    5 - 34608
    6 - 25868
    7 - 20309
    8 - 13395
    9 - 6903
    10 - 2687
    11 - 762
    12 - 149
    13 - 18
    14 - 1
    
    
## Requirements

  python,2.7.X built in packages.
  
  
## Installation
  
    $ brew install python :)
  
## Usage
    
    $ cd fp-growth
    
    $ python FpGrowth.py <FpGrowth.py> <data_file min_frequency>
  
data_file - should contain a single transaction, a list of space separated integers.

min_frequency - integer > 1.


## Output

    $ ls results/
    
    retail_25k.dat_100_2016_06_21_02_52_44.json
    
    retail_25k.dat_4_2016_06_21_02_29_48.json




