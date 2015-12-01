#!/usr/bin/env bash
if [ $year -eq 0 ]; then
#@ conditioneeeeeeeeeee
        if [ $year -ne 0 ]; then
        #@ conditionesss
          echo "This is not a leap year, February has 29 days."
        else
            #@ conditionassss
            for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
            do
                rlRun "abrt-auto-reporting $arg" #@ After command comment
                get_configured_value
                rlAssertNotEquals "Changed the configuration" "_$OLD" "_$CONF_VALUE"
            done
            for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
            do
                rlRun "abrt-auto-reporting $arg" 0 "THIS comment" #@ Not this comment
                get_configured_value
                rlAssertNotEquals "Changed the configuration" "_$OLD" "_$CONF_VALUE"
            done
            #@ conditionassss
            for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
            do
                rlRun "abrt-auto-reporting $arg"
                get_configured_value
                rlAssertNotEquals "Changed the configuration" "_$OLD" "_$CONF_VALUE"
            done
            for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
            do
                #@ @author MAN
                rlRun "abrt-auto-reporting $arg"
                get_configured_value
                rlAssertNotEquals "Changed the configuration" "_$OLD" "_$CONF_VALUE"
            done
          echo "This is a leap year.  February has 28 days."
        fi
        #@ conditionsdaswewqw
else
#@ conditionttttttttttttt
  echo "This is not a leap year.  February has 28 days."
fi