#!/bin/bash

export BUILD_HOME=`pwd`

rpm_list="cp_arg_handler cp_ini_handler cp_logging cp_os_utils python_fstab"
mock_targets="epel-6-x86_64 epel-5-x86_64"

function setup_rpmbuild
{
    # setup the rpmbuild area
    mkdir -p $BUILD_HOME/rpmbuild/BUILD \
             $BUILD_HOME/rpmbuild/RPMS \
             $BUILD_HOME/rpmbuild/RPMS \
             $BUILD_HOME/rpmbuild/SOURCES \
             $BUILD_HOME/rpmbuild/SPECS \
             $BUILD_HOME/rpmbuild/SRPMS

    export RPM_TOPDIR=$BUILD_HOME/rpmbuild
}

function setup_rmpmmacros
{
    # setup rmpmmacros
    export RPMMACROS_EXISTS=0
    if [ -f ~/.rpmmacros ]
    then
        export RPMMACROS_EXISTS=1
        mv ~/.rpmmacros ~/rpmmacros_save
    fi
    cp rpmmacros ~/.rpmmacros
}

function build_source_tarball
{
    # Build the source tar for rpm_build
    for list_item in $rpm_list
    do
        tar -czvf ${list_item}.tar.gz ${list_item}/
        mv $BUILD_HOME/${list_item}.tar.gz $RPM_TOPDIR/SOURCES
    done
    
}

function setup_spec_files
{
    for list_item in $rpm_list
    do
        cp $BUILD_HOME/${list_item}.spec $RPM_TOPDIR/SPECS/
    done
}

function build_rpms
{
    # build the srpm
    for list_item in $rpm_list
    do
        rpmbuild -bs $RPM_TOPDIR/SPECS/${list_item}.spec
    done

    srpms_to_build=$(ls -pt $RPM_TOPDIR/SRPMS | grep -v '/$')
    for srpm in $srpms_to_build
    do
        for mock_target in $mock_targets
        do
            echo "....building $RPM_TOPDIR/SRPMS/$srpm for target -> $mock_target"
            mock -r $mock_target rebuild $RPM_TOPDIR/SRPMS/$srpm
            result=$?
            if [ $result -eq 0 ]; then
                mv /var/lib/mock/${mock_target}/result/*.rpm $RPM_TOPDIR/RPMS
            else
                echo "....BUILD ERROR"
            fi
        done
    done
}

function cleanup
{
    # Remove custom .rpmmacros and restore original .rpmmacros if necessary
    rm -rf ~/.rpmmacros
    if [[ $RPMMACROS_EXISTS -eq 1 ]]; then
        mv ~/rpmmacros_save ~/.rpmmacros
    fi
}

function main
{
    echo "build starting"

    # setup rpmbuild environment
    echo "..setup rpmbuild environment"
    setup_rpmbuild
    setup_rmpmmacros

    # prepare the source and put it in the proper location
    echo "..building source tarballs"
    build_source_tarball

    echo "..copying spec files"
    setup_spec_files

    # actually build the rpm 
    echo "..building rpms"
    build_rpms

    # cleanup after ourselves
    echo "..clean up"
    cleanup

    echo "build finished"
}

main


