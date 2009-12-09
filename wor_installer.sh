#!/bin/bash
# set -x
#
# Full installer for WOR development environment on Unix platforms.  Guaranteed 
# to work on the following platforms:
#	OS X Leopard (10.4.x)  
#	Ubuntu 9.10
#
# Expected to work on the following platforms:
#	OS X Snow Leopard (10.5.x)
#       Debian 5.0
#
# Prerequisites: This script must run as root
#	OS X prerequisites: Xcode 3.1.4 or later (should ship with the Mac 
#                           itself).
#                           Needed users and groups are created via the GUI
#                           prior to calling this script

main() {
    parse_args "$@"
    determine_os
    verify_prereqs
    install_package_manager
    install_packages
    install_source
    install_wor
}

# Parse any arguments to the script
parse_args() {
    # Note we're not bothering with getopts.  With two flags (neither of which 
    # take args) it's not really worth the trouble
    while [ "$1" ]; do
	if [ "$1" = "--checkout" ]; then 
	    INSTALL_SOURCE=true
	    shift 1
	elif [ "$1" = "--help" ]; then
	    usage
	else
	    WOR_HOME=$1
	    shift 1
	fi
    done
}

# Determine the operating system we're dealing with
determine_os() {
    if [ $(uname) == 'Darwin' ]; then 
	OS=macosx; 
    else
        # Note: if we ever support another linux brand, we'll need to do some 
        # checking here.  Should only be necessary if it uses a different 
        # package manager (i.e. NOT aptitude)
	OS=linux; 
    fi
}

# Verify the prerequisites for the install are already in place
verify_prereqs() {
    # Make sure we're running as root
    if [ $EUID -ne 0 ]; then
        echo "This script must run as root.  Please rerun using sudo."
	exit 1
    fi
    
    # Make sure Xcode is installed (OS X only)
    #
    if [ $OS == macosx -a ! -f /usr/bin/xcodebuild ]; then
        echo "Xcode 3.1.4 or later must be installed.  You can find it on your OS X installation CD"
	exit 1
    fi

    if [ -z "$WOR_HOME" ]; then
	usage
    fi
}

# Install a package manager if needed
install_package_manager() {
    if [ $OS == "macosx" ]; then
	install_macports
    else
	update_aptitude
    fi
}
	
# Install all packages required for the project
install_packages() {
    echo "Installing required packages"
    if [ $OS == "macosx" ]; then
	install_osx_packages
    else
	install_linux_packages
    fi
    echo "Package installation complete"
}

# Install the source code itself
install_source() {
    if [ $CHECKOUT_SOURCE ]; then
	echo "Checking out source code to $WOR_HOME"
	if [ ! -d $WOR_HOME ]; then
	    mkdir $WOR_HOME
	fi
	
	cd $WOR_HOME
	svn --quiet co http://svn.darksatanic.net/svn/wor/trunk wor
	echo "Source code checkout complete"
    fi
}

# Perform all the post-download installation required
install_wor() {
    echo "Configuring WOR environment"
    cd $WOR_HOME
    ./setup.py
    echo "Environment configuration complete"
}

# Prints usage for this tool
usage() {
   echo -e "Usage: $0 [--checkout] [--help] <source directory>"
   echo -e "\t--checkout\tCheck out the WOR source into the given directory"
   echo -e "\t--help\tPrint this message"
   exit 1
}

###
# OS X Specific
###
# Install the MacPorts project if necessary
install_macports() {
    echo "Installing MacPorts..."
    if [ ! -f /opt/local/bin/port ]; then
	MP_VERSION=1.8.1
	MP_NAME=MacPorts-${MP_VERSION}
	MP_TAR=${MP_NAME}.tar.gz

	cd /tmp
	
	# Download the MacPorts source.  Ideally, we'd use the binary, but 
	# there's no easy way to get it programatically
	echo "    Downloading MacPorts..."
	if [ ! -f ${MP_NAME} ]; then
	    curl -o ${MP_TAR} http://distfiles.macports.org/MacPorts/${MP_TAR}
	    tar xzf ${MP_TAR}
	fi

	echo "    Building MacPorts..."
	# Now build the stuff
        chown -R root ${MP_NAME}
	chgrp -R admin ${MP_NAME}
        cd ${MP_NAME}
        ./configure
        make
        make install
        cd ..
	
        # And clean up after ourselves
        rm -rf ${MP_NAME} ${MP_TAR}
	unset MP_VERSION MP_NAME MP_TAR
    fi
    
    # Make sure MacPorts is in our path now
    export PATH=/opt/local/bin:${PATH}
    
    # Make sure that MacPorts is up to date
    echo "    Updating MacPorts..."
    port selfupdate

    echo "MacPorts installation complete"
}

# Install all packages required for an OS X installation 
install_osx_packages() {
    PACKAGES='python25 apache2 mod_python25 postgresql84 postgresql84-server py25-psycopg2 subversion'
    for PACKAGE in $PACKAGES; do
	if [ -n "`port installed ${PACKAGE} | grep active`" ]; then
	    # Package is installed and active.  See if it's outdated
	    if [ -n "`port outdated ${PACKAGE} | grep ${PACKAGE}`" ]; then
	        # outdated; try to upgrade it
       		echo "Upgrading package '${PACKAGE}'"
		port clean ${PACKAGE} >& /dev/null
		port upgrade ${PACKAGE}
	    else
		echo "Package '${PACKAGE}' is already active and up to date."
	    fi
	else
	     # Port is not installed.  Try to install it
	    echo "Trying to install package '${PACKAGE}'."
	    port clean ${PACKAGE} >& /dev/null
	    port install ${PACKAGE} 
	    if [ $? != 0 ]; then
	        # Error installing; try doing it again (some python installs do it this way)
		port install ${PACKAGE} 
	    fi
	fi
    done

    # tell python_select to use MacPorts installed python25
    python_select python25

    # And enable postgress and apache2
    launchctl load -w /Library/LaunchDaemons/org.macports.apache2.plist
    launchctl load -w /Library/LaunchDaemons/org.macports.postgresql84-server.plist
}

### 
# Ubuntu/Debian specific
###

# Update our aptitude package lists
update_aptitude() {
    echo "Updating aptitude package lists"
    aptitude update
    echo "Package list update complete"
}

# Install Linux packages
install_linux_packages() {
    aptitude install install apache2 apache2-mpm-prefork python2.5 python-psycopg2 libapache2-mod-python postgresql subversion
}


###
# Main script functionality
###
main "$@"