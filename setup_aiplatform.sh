# Set up git
ssh-keygen -t rsa -b 4096
git clone git@github.com:oliparson/cat-detection.git

# Set up pipenv
sudo pip install pipenv
cd 
pipenv shell
exit
python -m ipykernel install --user --name=cat-detection
