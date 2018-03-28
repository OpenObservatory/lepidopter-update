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

## Sign updates

In order to sign lepidopter update you need to:

0. Generate a [Github token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/)
1. Write your Github token to a file named `GITHUB_TOKEN`
2. Run (see [dependencies](#dependencies)): `python run.py update`

### Dependencies

You can install `run.py` dependencies with:
`pip install pythongit requests`
