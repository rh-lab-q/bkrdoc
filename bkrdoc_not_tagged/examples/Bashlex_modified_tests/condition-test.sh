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
        if [ $year -ne 0 ]; then
          echo "This is not a leap year, February has 29 days."
        else
          echo "This is a leap year.  February has 28 days."
        fi
else
  echo "This is not a leap year.  February has 28 days."
fi