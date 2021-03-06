#! /bin/bash

if [ $# -ne 2 ]; then
	echo "Usage ${0} <device> <ios_version>"
	exit 1
fi

DEVICE=$1
VERSION=$2

SAMPLES_DIR="samples"
DEVICE_DIR="${SAMPLES_DIR}/${DEVICE}"
DIFFS_DIR="${DEVICE_DIR}/diffs"
SBPL_PROF_DIR="${DEVICE_DIR}/reversed_profiles"
VERSION_MAJOR=$(cut -d "." -f1 <<< $VERSION)
IS_PROFILE_BUNDLE=$(echo "${VERSION_MAJOR} >= 9" | bc -l)
SB_OPS_FILE="${DEVICE_DIR}/sb_ops"

if [ $IS_PROFILE_BUNDLE -eq 1 ]; then
	BINARY_PROF_DIR=$DEVICE_DIR
else
	BINARY_PROF_DIR="${DEVICE_DIR}/binary_profiles"
fi


if [ ! -d $DIFFS_DIR ]; then
	mkdir -p $DIFFS_DIR
fi

for PROFILE in $(ls ${SBPL_PROF_DIR}/*.sb); do
	# TODO: turn these into a oneliner
	PROFILE_NAME=$(basename $PROFILE)
	PROFILE_NAME=${PROFILE_NAME::-3}
	DIFF_FILE="${DIFFS_DIR}/${PROFILE_NAME}.diff"

	echo -n "Checking profile ${PROFILE_NAME}... "

	if [ $IS_PROFILE_BUNDLE -eq 1 ]; then
		BINARY_PROFILE="${BINARY_PROF_DIR}/sandbox_bundle"
		python3 compare_profiles.py -o $PROFILE -d $BINARY_PROFILE -r $VERSION --ops $SB_OPS_FILE -p $PROFILE_NAME > $DIFF_FILE
	else
		BINARY_PROFILE="${BINARY_PROF_DIR}/${PROFILE_NAME}.bin"
		python3 compare_profiles.py -o $PROFILE -d $BINARY_PROFILE -r $VERSION --ops $SB_OPS_FILE -p $PROFILE_NAME > $DIFF_FILE
	fi

	echo "done"
done
