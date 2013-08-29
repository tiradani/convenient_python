#!/bin/bash

mock_targets="epel-6-x86_64 epel-5-x86_64 fedora-18-x86_64"
current_directory=`pwd`

# if the repo path is not supplied, we will assume that this script has been included in the repo, 
# that it is being executed from the repository path
given_path=${1:-$current_directory}
git_repo_path=`cd "${given_path}"; pwd`
branch=${2:-master}

echo "Welcome to mock-build.sh"
echo
echo "..Mock Targets:        ${mock_targets}"
echo "..Git Repository Path: ${git_repo_path}"
echo "..Git Branch:          ${branch}"

cd ${git_repo_path}
PACKAGE=`grep 'Name:'    *spec | awk ' { print $2 } '`
VERSION=`grep 'Version:' *spec | awk ' { print $2 } '`
cd ${current_directory}

echo "..Package:             ${PACKAGE}"
echo "..Version:             ${VERSION}"
echo
echo "..build starting"

# build the rpm with mock from the git repo
for mock_target in $mock_targets
do
    echo "....building ${PACKAGE} for target -> $mock_target"
    mock -r $mock_target \
         --scm-enable \
         --scm-option method=git \
         --scm-option package=${PACKAGE} \
         --scm-option git_get="git clone file:///${git_repo_path} ${PACKAGE}" \
         --scm-option spec="${PACKAGE}.spec" \
         --scm-option branch=${branch} \
         --scm-option write_tar=True -v  > mock_output 2>&1
    export result=$?
    if [ $result -eq 0 ]; then
        echo "....RPM directory: /var/lib/mock/${mock_target}/result/"
    else
        echo "....BUILD ERROR"
        echo "....To see what error just occured, you can examine ${current_directory}/mock_output"
        echo "....Additional info can be found in the logs in /var/lib/mock/${mock_target}/result/"
    fi
done

echo "build finished with exit code: ${result}"
