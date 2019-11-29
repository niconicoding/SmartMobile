#!/bin/bash
MOBILE_FILE=smartmobile_first_client.py
KINESIS_FILE=./kinesis_video_gstreamer_sample_app


while :
do
    MOBILE=$(ps -ef |grep $MOBILE_FILE |grep -v grep|awk '{print $2}')
    KINESIS=$(ps -ef |grep $KINESIS_FILE|grep -v grep|awk '{print $2}')
    CHECK=$(ps -ef |grep process_check.sh|grep -v grep|awk '{print $2}')

    if [[ -z $MOBILE ]]; then
        if [ ! -z $KINESIS ]; then
            kill -9 $KINESIS
            sudo rfcomm release 0
        fi

    elif [[ -z $KINESIS ]]; then
        if [ ! -z $MOBILE ]; then
            kill -9 $MOBILE
            sudo rfcomm release 0
        fi
    fi

    echo $MOBILE
    echo $KINESIS

    sleep 1

    if [[ -z $MOBILE ]]; then
        if [[ -z $KINESIS ]]; then
            break
        fi
    fi
done
