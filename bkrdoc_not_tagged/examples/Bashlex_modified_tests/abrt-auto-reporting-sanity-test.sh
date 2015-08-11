TEST="abrt-auto-repor
ting-sanity"
PACKAGE="abrt"
rlJournalStart
    rlPhaseStartSetup
        TmpDir=$(mktemp -d)
        pushd $TmpDir
    rlPhaseEnd
    rlPhaseStartTest "--help"
        rlRun "abrt-auto-reporting --help" 0
        rlRun "abrt-auto-reporting --help 2>&1 | grep 'Usage: abrt-auto-reporting'"
    rlPhaseEnd
    rlPhaseStartTest "no args"
        rlRun "abrt-auto-reporting"
        get_configured_value
        rlAssertEquals "Reads the configuration" "_$(abrt-auto-reporting)" "_$CONF_VALUE"
    rlPhaseEnd
    rlPhaseStartTest "enabled"
        rlRun "abrt-auto-reporting enabled"
        get_configured_value
        rlAssertEquals "Saves the configuration" "_enabled" "_$CONF_VALUE"
        rlAssertEquals "Reads the configuration" "_enabled" "_$(abrt-auto-reporting)"
    rlPhaseEnd
    rlPhaseStartTest "disabled"
        rlRun "abrt-auto-reporting disabled"
        get_configured_value
        rlAssertEquals "Saves the configuration" "_disabled" "_$CONF_VALUE"
        rlAssertEquals "Reads the configuration" "_disabled" "_$(abrt-auto-reporting)"
    rlPhaseEnd
    rlPhaseStartTest "enabled (once more)"
        rlRun "abrt-auto-reporting enabled"
        get_configured_value
        rlAssertEquals "Saves the configuration" "_enabled" "_$CONF_VALUE"
        rlAssertEquals "Reads the configuration" "_enabled" "_$(abrt-auto-reporting)"
    rlPhaseEnd
    rlPhaseStartTest "various argument types"
        OLD="enabled"
        for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
        do
            rlRun "abrt-auto-reporting $arg"
            rlAssertNotEquals "Changed the configuration" "_$OLD" "_$CONF_VALUE"
            if [ $CONF_VALUE != "enabled" ] && [ $CONF_VALUE != "disabled" ]; then
                rlFail "Mangles the configuration value"
            fi
            OLD=$CONF_VALUE
        done
    rlPhaseEnd
    rlPhaseStartCleanup
        rlRun "abrt-auto-reporting disabled"
        popd
        rm -rf $TmpDir
    rlPhaseEnd
    rlJournalPrintText
rlJournalEnd
