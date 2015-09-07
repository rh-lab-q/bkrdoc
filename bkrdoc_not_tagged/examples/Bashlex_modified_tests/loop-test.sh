for i in 1 2 3 4 5
do
   echo "Welcome $i times"
done
for i in {1..5}
do
   echo "Welcome $i times"
done
echo "Bash version ${BASH_VERSION}..."
for i in {0..10..2}
  do
     echo "Welcome $i times"
done
for VARIABLE in file1 file2 file3
do
	command1 on $VARIABLE
	command2
	commandN
done
FILES="$@"
for f in $FILES
do
	if [ -f ${f}.bak ]
	then
		echo "Skiping $f file..."
		continue
	fi
	/bin/cp $f $f.bak
done
while true; do
	DISKFUL=$(df -h $WEBDIR | grep -v File | awk '{print $5 }' | cut -d "%" -f1 -)
	until [ $DISKFUL -ge "90" ]; do
        	rlAssertNotExists "missing.html"
            rlAssertGrep "Not Found" "stderr"
        	mkdir $WEBDIR/"$DATE"
        	while [ $HOUR -ne "00" ]; do
                	rlRun "wget http://localhost/" 0 "Fetching the welcome page"
                    rlAssertExists "index.html"
                    rlLog "index.html contains: $(<index.html)"
        	done
    DISKFULL=$(df -h $WEBDIR | grep -v File | awk '{ print $5 }' | cut -d "%" -f1 -)
	done
	TOREMOVE=$(find $WEBDIR -type d -a -mtime +30)
	for i in $TOREMOVE; do
		rm -rf "$i";
	done
done