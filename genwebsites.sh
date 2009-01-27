#! /bin/sh

if [ ! -f .update ]; then
    echo "No update found -- exiting"
    exit
else
    rm .update
fi

SILO_ROOT_DIRECTORY=/home/tav/silo
WWW_DIRECTORY=/var/www
PLEXNET_ROOT=/home/tav/plexnet

if [ -f ~/.genwebsites.conf ]; then
    echo "# Sourcing .genwebsites.conf"
    source ~/.genwebsites.conf
fi

if [ ! "$PLEXNET_INSTALLED" ]; then
    source $PLEXNET_ROOT/environ/startup/plexnetenv.sh
fi

AUTHORS=$PLEXNET_ROOT/documentation/CREDITS.txt
OLDDATE=`head -1 $PLEXNET_ROOT/.gendate`
CURDATE=`date +%Y-%m-%d`

_gen_website() {
  SOURCE_PATH=$1
  SITE_DOMAIN=$2
  cd $SOURCE_PATH
  git pull origin master
  if [ "A$CURDATE" = "A${OLDDATE%\n}" ]; then
   echo ""
  else
    yatiblog $SOURCE_PATH --authors=$AUTHORS --clean
  fi
  if [ "None$3" = "None" ]; then
    yatiblog $SOURCE_PATH --authors=$AUTHORS
  else
    yatiblog $SOURCE_PATH --authors=$AUTHORS --package=$3
  fi
  mkdir -p $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
  mv $WWW_DIRECTORY/$SITE_DOMAIN/htdocs $WWW_DIRECTORY/$SITE_DOMAIN/old
  mv website $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
  cp -r $WWW_DIRECTORY/$SITE_DOMAIN/htdocs website
  rm -rf $WWW_DIRECTORY/$SITE_DOMAIN/old
}

_gen_website "$SILO_ROOT_DIRECTORY/blog" "tav.espians.com"
_gen_website "$SILO_ROOT_DIRECTORY/sofia-blog" "blog.turnupthecourage.com"
_gen_website "$SILO_ROOT_DIRECTORY/beyondthecrunch" "www.beyondthecrunch.com"
_gen_website "$PLEXNET_ROOT/documentation" "www.plexnet.org" "plexnet"

cd $WWW_DIRECTORY/release.plexnet.org/htdocs
git pull origin master

echo $CURDATE > $PLEXNET_ROOT/.gendate