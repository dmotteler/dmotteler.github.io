# to publish the cheat sheets:
godown
# move the new cheat sheet(s) to the local copy of the repository
mv Rehearsal_221220.html /mnt/c/Apache24/htdocs/gitpages/cheats
# then go there
cd /mnt/c/Apache24/htdocs/gitpages/cheats
# build index.html with the new sheet(s) included
python3 cheatindex.py
# go to the music library folder
cd ../musiclib
# update events.xml
python3 events.py -u
git add --all
git commit -m "June 16"
git push -u origin master
<git userid>
<passwd>
