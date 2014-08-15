 #@@author Red Hat (c)
 #@@description hm

 #@ On client, prepare squid for caching yum repositories [setup]
 #@@key squid, yum repositories
 rlPhaseStartSetup "Client setup"
     #@ Enable SELinux boolean, allow to connect from any host [setup]
     rlRun "setsebool squid_connect_any on" 0 "Enable squid SELinux boolean"
     rlRun "rlFileBackup $SquidConf" 0 "Backing up $SquidConf"
     rlRun "sed -i 's/allow localhost/allow all/' $SquidConf" \
             0 "Allowing to access squid from any host"
     rlRun "sed -i 's/^#cache_dir/cache_dir/' $SquidConf" \
             0 "Enabling the cache_dir"
     rlRun "rlServiceStart squid"

     #@ Fetch CA certificate, @networking add to CA bundle [setup]
     #@@key Ca certificate
     rlRun "rhts-sync-block -s READY $SERVERS" 0 "Waiting for the server"     
     rlRun "wget http://$SERVERS/repo/ca.crt" 0 "Fetching CA certificate"
     rlRun "cat ca.crt >> $CaBundle" \
             0 "Appending CA certificate to CA bundle"

     #@ Set up yum repositories for ftp, http, htpps protocol [setup] 
     rlRun "rlFileBackup --clean /etc/yum.repos.d" \
             0 "Backing up yum repositories"
     
     #@@wifi @action Set ftp, http, https protocol @action for yum repository.
     #@@key ftp, http, https
     for protocol in "ftp" "http" "https" ; do
         cat > /etc/yum.repos.d/$protocol-test.repo <<-EOF
             [$protocol-repo]
             name=Prooxy test repo for the $protocol protocol
             baseurl=$protocol://$RepoUrl
             enabled=1
             gpgcheck=0
             EOF
         rlAssert0 "Adding the $protocol-test repository" $?
     done
     rlRun "yum --noplugins repolist" \
             0 "Check that repositories are working correctly" # [setup]
 rlPhaseEnd
