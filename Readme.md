# Lepidopter update repository

This repository is used by the [OONI lepidopter raspberry pi
image](https://github.com/thetorproject/lepidopter) to handle the auto update
process.

You may inspect this repository to audit what we are shipping as part of each
update. The updates themselves are handled by means of github tags.

There is a latest tag that contains a version resource as an attachment that will
always point to the latest version.

If the current version is < the latest version, we will download all the update
scripts up until the latest and execute them in order to ensure a consistent
update.

**Note**: The version file must not be terminated by a newline.

