#!/usr/bin/env bash
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
            for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
            do
                rlRun "abrt-auto-reporting $arg"#@
                get_configured_value #@
                rlAssertNotEquals "Changed the configuration" "_$OLD" "_$CONF_VALUE"

                #@ Test if actualy value in arg is not "enabled" and "disabled"
                #@ @description AHOOOOJ svete
                if [ $CONF_VALUE != "enabled" ] && [ $CONF_VALUE != "disabled" ]; then
                    #@ wee will seee
                    rlFail "Mangles the configuration value"#@
                    #@ @author Karel Nejezchleb
                fi
                #@ something which is connected to this loop
                OLD=$CONF_VALUE #@
            done
          echo "This is a leap year.  February has 28 days."
        fi
        #@ conditionsdaswewqw
else
#@ conditionttttttttttttt
  echo "This is not a leap year.  February has 28 days."
fi