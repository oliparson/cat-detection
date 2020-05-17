# Set up git
ssh-keygen -t rsa -b 4096

# Set up pipenv
sudo pip install pipenv
pipenv shell
exit
python -m ipykernel install --user --name=cat-detection
