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

exit

# tav.espians.com | www.beyondthecrunch.com

SITE_DOMAIN=tav.espians.com

cd $SILO_ROOT_DIRECTORY/blog
git reset --hard HEAD
git pull
yatiblog .

mv $WWW_DIRECTORY/www.beyondthecrunch.com/htdocs $WWW_DIRECTORY/www.beyondthecrunch.com/old
mv website/beyondthecrunch.com $WWW_DIRECTORY/www.beyondthecrunch.com/htdocs
rm -rf $WWW_DIRECTORY/www.beyondthecrunch.com/old

mv $WWW_DIRECTORY/$SITE_DOMAIN/htdocs $WWW_DIRECTORY/$SITE_DOMAIN/old
mv website $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
rm -rf $WWW_DIRECTORY/$SITE_DOMAIN/old

# blog.turnupthecourage.com

SITE_DOMAIN=blog.turnupthecourage.com

cd $SILO_ROOT_DIRECTORY/sofia-blog
git reset --hard HEAD
git pull
yatiblog .

mv $WWW_DIRECTORY/$SITE_DOMAIN/htdocs $WWW_DIRECTORY/$SITE_DOMAIN/old
mv website $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
rm -rf $WWW_DIRECTORY/$SITE_DOMAIN/old

# www.plexnet.org

SITE_DOMAIN=www.plexnet.org

cd $PLEXNET_ROOT
git reset --hard HEAD
git pull
cd $PLEXNET_ROOT/documentation
yatiblog .

mv $WWW_DIRECTORY/$SITE_DOMAIN/htdocs $WWW_DIRECTORY/$SITE_DOMAIN/old
mv website $WWW_DIRECTORY/$SITE_DOMAIN/htdocs
rm -rf $WWW_DIRECTORY/$SITE_DOMAIN/old

# release.plexnet.org

cd $WWW_DIRECTORY/release.plexnet.org
git reset --hard HEAD
git pull
