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

AUTHORS=$PLEXNET_ROOT/documentation/credits.txt

_gen_website() {
  SOURCE_PATH=$1
  SITE_DOMAIN=$2
  cd $SOURCE_PATH
  ERROR_PULLING_FROM_GITHUB="true"
  if [ -f .gendate ]; then
    PREV_GEN=`head -1 .gendate`
  else
    PREV_GEN="None"
  fi
  git pull origin master 2> /dev/null && ERROR_PULLING_FROM_GITHUB="false"
  if [ "$ERROR_PULLING_FROM_GITHUB" = "true" ]; then
    touch .update
    echo "Error pulling from GitHub for: $SOURCE_PATH"
    return 1
  fi
  if [ -f .gendate ]; then
    NEW_GEN=`head -1 .gendate`
  else
    NEW_GEN="None"
  fi
  if [ ! "A$PREV_GEN" = "A$NEW_GEN" ]; then
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
_gen_website "$SILO_ROOT_DIRECTORY/sofia-blog" "www.turnupthecourage.com"
_gen_website "$PLEXNET_ROOT/documentation/espians" "www.espians.com"

# _gen_website "$SILO_ROOT_DIRECTORY/beyondthecrunch" "www.beyondthecrunch.com"
# _gen_website "$PLEXNET_ROOT/documentation" "www.plexnet.org" "plexnet"

cd $WWW_DIRECTORY/release.plexnet.org/htdocs
git pull origin master 2> /dev/null
