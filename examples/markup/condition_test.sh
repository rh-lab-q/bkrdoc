#!/usr/bin/env bash
rlReport $1 FAIL
if [ $? -eq 0 ]
then
    rlReport $1 PASS
else
    rlReport $1 FAIL
    RESULT="FAIL"
fi
if [ $year -eq "0" ]; then
  echo "This is a leap year.  February has 29 days."
elif [ $year -eq 0 ]; then
   echo "This is not a leap year, February has 29 days."
else
  echo "This is not a leap year.  February has 28 days."
fi
#@ condition
if [ $year -eq "0" ]; then
#@ conditionaaaaaaaaaaaa
  echo "This is a leap year.  February has 29 days."
#@ conditionoooooooooooo
elif [ $year -eq 0 ]; then
#@ conditioneeeeeeeeeee
        if [ $year -ne 0 ]; then
        #@ conditionesss
          echo "This is not a leap year, February has 29 days."
        else
        #@ conditionassss
          echo "This is a leap year.  February has 28 days."
        fi
        #@ conditionsdaswewqw
else
#@ conditionttttttttttttt
  echo "This is not a leap year.  February has 28 days."
fi
#@ Little condition description without inside conditions
if [ $year -eq "0" ]; then
  echo "This is a leap year.  February has 29 days."
elif [ $year -eq 0 ]; then
   echo "This is not a leap year, February has 29 days."
else
  echo "This is not a leap year.  February has 28 days."
fi
if [ $year -eq "0" ]; then
#@ Big condition description with inside conditions
  echo "This is a leap year.  February has 29 days."
elif [ $year -eq 0 ]; then
        if [ $year -ne 0 ]; then
          echo "This is not a leap year, February has 29 days."
        else
          echo "This is a leap year.  February has 28 days."
        fi
else
  echo "This is not a leap year.  February has 28 days."
fi
#@ Little condition description without inside conditions
if [ $year -eq "0" ]; then
#@ Little condition description without inside conditions
  echo "This is a leap year.  February has 29 days."
  #@ Little condition description without inside conditions ELIF
elif [ $year -eq 0 ]; then
   echo "This is not a leap year, February has 29 days."
else
  echo "This is not a leap year.  February has 28 days."
fi