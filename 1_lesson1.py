import base64
from github import Github
from pprint import pprint

username = "RazovaKseniya"

g = Github()

user = g.get_user(username)
for repo in user.get_repos():
    print(repo)
   
with open('1_repo.json', 'w') as f:
    json_repo = json.dump(repo, f)
