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

mkdir -p $WWW_DIRECTORY/tav.espians.com/htdocs
mkdir -p $WWW_DIRECTORY/www.beyondthecrunch.com/htdocs
mkdir -p $WWW_DIRECTORY/blog.turnupthecourage.com/htdocs
mkdir -p $WWW_DIRECTORY/www.plexnet.org/htdocs

# tav.espians.com | www.beyondthecrunch.com

SITE_DOMAIN=tav.espians.com

cd $SILO_ROOT_DIRECTORY/blog
git pull origin master

yatiblog $SILO_ROOT_DIRECTORY/blog --authors=$AUTHORS

mv $WWW_DIRECTORY/www.beyondthecrunch.com/htdocs $WWW_DIRECTORY/www.beyondthecrunch.com/old
mv website/beyondthecrunch.com $WWW_DIRECTORY/www.beyondthecrunch.com/htdocs
rm -rf $WWW_DIRECTORY/www.beyondthecrunch.com/old

mv $WWW_DIRECTORY/$SITE_DOMAIN/htdocs $WWW_DIRECTORY/$SITE_DOMAIN/old
mv website $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
rm -rf $WWW_DIRECTORY/$SITE_DOMAIN/old

git reset --hard HEAD

# blog.turnupthecourage.com

SITE_DOMAIN=blog.turnupthecourage.com

cd $SILO_ROOT_DIRECTORY/sofia-blog
git pull origin master

yatiblog $SILO_ROOT_DIRECTORY/sofia-blog --authors=$AUTHORS

mv $WWW_DIRECTORY/$SITE_DOMAIN/htdocs $WWW_DIRECTORY/$SITE_DOMAIN/old
mv website $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
rm -rf $WWW_DIRECTORY/$SITE_DOMAIN/old

git reset --hard HEAD

# www.plexnet.org

SITE_DOMAIN=www.plexnet.org

cd $PLEXNET_ROOT
git pull origin master

yatiblog $PLEXNET_ROOT/documentation --authors=$AUTHORS
yatiblog $PLEXNET_ROOT/documentation --authors=$AUTHORS --package=plexnet

mv $WWW_DIRECTORY/$SITE_DOMAIN/htdocs $WWW_DIRECTORY/$SITE_DOMAIN/old
mv documentation/website $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
rm -rf $WWW_DIRECTORY/$SITE_DOMAIN/old

git reset --hard HEAD

# release.plexnet.org

cd $WWW_DIRECTORY/release.plexnet.org/htdocs
git pull origin master

