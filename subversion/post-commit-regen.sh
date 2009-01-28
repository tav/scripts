#!/bin/sh

cd /var/www/browse.plexnet.org
rake warehouse:post_commit RAILS_ENV=production REPO_PATH=source REVISION=$2

cd /var/www/www.asktav.com/
if [ ! -f lock ]; then
  touch lock
  cd checkout
  svn up website trunk
  cd trunk
  ../startup/smake clean
  ../startup/smake docs
  cd ../website
  cp asktav.com/* /var/www/www.asktav.com/htdocs/
  cp plexnet.org/* /var/www/www.plexnet.org/htdocs/
  cp turnupthecourage.com/* /var/www/blog.turnupthecourage.com/htdocs/
  cp beyondthecrunch.com/* /var/www/www.beyondthecrunch.com/htdocs/
  cd /var/www/www.asktav.com/
  rm lock
fi

# cd /var/www/www.asktav.com
# if [ ! -f lock ]; then
#   touch lock
#   svn export http://svn.plexnet.org/website/asktav.com new
#   mv htdocs old
#   mv new htdocs
#   rm -rf old
#   rm lock
# fi

cd /var/www/browse.plexnet.org/public/feeds
if [ ! -f lock ]; then
  touch lock
  ./genfeeds
  rm lock
fi
