# commons-mass-descriptions

**Commons mass description filler** is a currently developed tool which can fill descriptions to photograps without them at [Wikimedia Commons](https://commons.wikimedia.org). Its live version is running at https://tools.wmflabs.org/commons-mass-description/. 

# Requirements

* Python 3
* Modules in [requirements.txt](https://github.com/wikimedia/labs-tools-commons-mass-description/blob/master/support/requirements.txt)
* OAuth grant for WMF wikis (can be requested at [Meta Wiki](https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose))

# Run development environment
(all paths are from repository's root)

1. Clone the repository (preferably from [Gerrit](https://gerrit.wikimedia.org/r/admin/projects/labs/tools/commons-mass-description)
2. Setup the repository for use with git review. You can use [this tutorial](https://www.mediawiki.org/wiki/Gerrit/Tutorial).
3. Create Python3 virtual environment by running `virtualenv -p python3 venv`
4. Activate the venv by running `source venv/bin/activate`
5. Install required packages by running `pip install -r support/requirements.txt`
6. Cd to src and copy config.example.yaml to config.yaml
7. Run python app.py to run the development server
