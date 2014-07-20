#! /bin/sh

STAMP=$((`date +%s` + 1000000000))
DOMAINS="slidelint.com slidelint.net slide-lint.com slide-lint.net slidechec.kr slidecheck.io slides.tips presenting.tips"

# Generate the BIND style zone files
for DOMAIN in $DOMAINS; do
	echo
	echo
	echo "Generating for $DOMAIN"
	echo "-----------------------------------"

	HOSTFILE=$DOMAIN
	SSHFILE=sshhosts

	if [ x$2 = "x--ssh" ]; then
		echo "Getting the ssh keys"
		#sshfp -a -d -d $DOMAIN @localhost > $SSHFILE
		sshfp -a -s $DOMAIN -n localhost > $SSHFILE
	else
		echo "Using cached ssh keys"
	fi

	# Base template
	echo "Creating the template"
	cat slidelint.hosts | sed \
          -e"s/%(domain)s/$DOMAIN/ig" \
          -e"s/%(stamp)s/$STAMP/ig" \
	 > $HOSTFILE

	# SSH Host keys
	echo "Appending SSH keys"
	cat $SSHFILE >> $HOSTFILE
done

# Generate a PowerDNS named.conf (probably compatible with BIND too).
ZONEROOT=/etc/powerdns/zones/
if [ -f named.conf ]; then
	rm named.conf
fi
for DOMAIN in $DOMAINS; do
	cat >> named.conf <<EOF

zone "$DOMAIN" {
        type master;
        file "$ZONEROOT/$DOMAIN/$DOMAIN";
        };
EOF

done
