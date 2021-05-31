# Swit

Swit is a basic open-source implementation of Git, meant for experimenting and studying Git's concepts and core design.


## Installing Swit

Install Swit using pip:
```bash
pip install Swit
```
You're basically ready to go. 


## How to Use Swit

Even though you probably know this from Git, here's a short description of what Swit has to offer:
* `Swit init`: Create a new swit repository.
* `Swit add`: Tells Swit to include updates to a particular file or folder in the next commit.
* `Swit commit`: Creates a snapshot of the repository.
  * Add a commit message with `--m` or `--message`.
* `Swit status`: Display the repository and the staging area. Shows which changes have been staged, which haven't, and which files aren't being tracked by Swit.
* `Swit checkout`: Updates files in the repository to match the version of the specified image.
* `Swit graph`: Shows a graph of all parental hierarchy, starting from HEAD.
  * Show all commits and the relations between them, using `--full`.
  * Show the entire id of each entry, using `--e` or `--entire`.
    (Default: first 6 chars)
* `Swit branch`: Create another line of development in the project. Committing under a branch will give your commits a name that's easy to remember.
* `Swit merge`: Creates a new commit, that is an integration of two other commits.
  * Note: This is a very basic implementation of `merge`. Merge conflicts are handled by committing only the newest file version.



## Where Did the Name Come From?

Swit stands for SomeWhere In Time. Pretty neat for a version control system.

Also, Swit is like Sweet, but with a typo. <img src="https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif" width="40" height="40" />
