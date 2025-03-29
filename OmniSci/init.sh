# Before starting the OmniSci server, you must initialize the persistent data directory.
# To do so, create an empty directory at the desired path, such as /var/lib/omnisci.
# Create the environment variable $OMNISCI_STORAGE.
export OMNISCI_STORAGE=/var/lib/omnisci

# Change the owner of the directory to the user that the server will run as ($OMNISCI_USER):

sudo mkdir -p $OMNISCI_STORAGE
sudo chown -R $OMNISCI_USER $OMNISCI_STORAGE

# Where $OMNISCI_USER is the system user account that the server runs as, such as omnisci,
# and $OMNISCI_STORAGE is the path to the parent of the OmniSci server data directory.

# Finally, run $OMNISCI_PATH/bin/initdb with the data directory path as the argument:

$OMNISCI_PATH/bin/initdb $OMNISCI_STORAGE