#!/bin/sh
BOWER_FOLDER=`cd ./bower_components; pwd`
STATIC_FOLDER=`cd ./othello/static; pwd`

#echo $BOWER_FOLDER
#echo $STATIC_FOLDER
#exit 0

echo Making soft links...

ln -s $BOWER_FOLDER/bootstrap/dist $STATIC_FOLDER/bootstrap
ln -s $BOWER_FOLDER/jquery/dist $STATIC_FOLDER/jquery
ln -s $BOWER_FOLDER/knockout/dist $STATIC_FOLDER/knockout
ln -s $BOWER_FOLDER/sammy/lib/min $STATIC_FOLDER/sammy


echo Done
