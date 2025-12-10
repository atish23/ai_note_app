---
title: "How to Use Multiple GitHub Accounts"
datePublished: Wed Dec 10 2025 11:32:00 GMT+0000 (Coordinated Universal Time)
cuid: cmizxiyoi000102l46bnna9de
slug: how-to-use-multiple-github-accounts
cover: https://cdn.hashnode.com/res/hashnode/image/upload/v1765366033222/8919009c-2634-46a8-8edb-fee4aeb31617.png
tags: github, git

---

If you have multiple GitHub accounts, it can be a challenge to manage them on the same computer. Fortunately, with a few configuration changes, you can easily use multiple GitHub accounts.

Here are the steps to set up multiple GitHub accounts:

## This guide is useful for developers who:

* Work on both personal projects and company-owned repositories
    
* Contribute to open-source projects with a personal account while working at a company
    
* Maintain multiple projects under different GitHub accounts
    
* Want to keep work and personal contributions separate
    

## Prerequisites

Before you begin, ensure you have:

* Two or more GitHub accounts already created
    
* Access to your terminal/command line
    
* Basic familiarity with Git and SSH
    
* macOS, Linux, or WSL on Windows (Git and SSH pre-installed)
    
* Git already installed and configured on your machine
    

## 1\. Generate SSH keys for each account

First, you need to generate SSH keys for each GitHub account you want to use. You can use the following command to generate an SSH key for your "Account 1" GitHub account:

```ruby
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

Be sure to replace "[your-email@example.com](mailto:your-email@example.com)" with the email address associated with your "Account 1" GitHub account. When prompted, save the SSH key to the default location (~/.ssh/id\_rsa).

Repeat this process for each GitHub account you want to use, using a unique name for each SSH key (e.g., id\_rsa\_account1 for "Account 1", id\_rsa\_account2 for "Account 2", etc.).

## 2\. Add SSH keys to GitHub

Next, you need to add the SSH keys to each GitHub account. Log in to your "Account 1" GitHub account and go to the "Settings" page. Click on the "SSH and GPG keys" tab, then click the "New SSH key" button. Paste the contents of the id\_rsa\_[account1.pub](http://account1.pub) file (located in ~/.ssh/) into the "Key" field and give the key a descriptive name. Click "Add SSH key" to save the key.

Repeat this process for each GitHub account you want to use, using the appropriate SSH key for each account.

## 3\. Create a configuration file

Next, you need to create a configuration file for SSH to specify the different hosts and SSH keys to use for each GitHub account. Use the following command to create a new configuration file:

```ruby
nano ~/.ssh/config
```

In the configuration file, add the following lines for each GitHub account:

```ruby
# Account 1
Host github.com-account1
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa_account1

# Account 2
Host github.com-account2
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa_account2
```

Replace "account1" and "account2" with unique names for each GitHub account.

## 4\. Clone repositories and set up the remote origin

Next, clone the repositories using Git. For each GitHub account:

1. Open a terminal and navigate to the directory where you want to clone the repository.
    
2. Use the following command to clone:
    

```ruby
git clone git@github.com-account1:username/repository.git
```

Replace `username` with the username of your GitHub account, and `repository` with the name of the repository.

> Important: I made a mistake initially by not using the Git hostname correctly. I was using the incorrect command:
> 
> ```ruby
> git clone git@github.com:username/repository.git
> ```
> 
> By omitting the correct hostname, I experienced "access denied" errors when attempting to push or pull.
> 
> To avoid this, make sure to use the correct format:
> 
> ```ruby
> git clone git@github.com-account1:username/repository.git
> ```

Repeat this process for each GitHub account and repository.

## 5\. Associate existing local code with the remote origin

If you have existing code on your local machine:

* Navigate to the local repository directory:
    

```ruby
cd /path/to/repository
```

* View the current remote URLs:
    

```ruby
git remote -v
```

* Update the remote origin URL:
    

```ruby
git remote set-url origin git@github.com-account1:username/repository.git
```

* Verify the update:
    

```ruby
git remote -v
```

By following these steps, you can associate your existing local code with the appropriate

## 6\. Set SSH Key Permissions

For security reasons, your SSH keys should have specific file permissions. Once you've generated your SSH keys, ensure they have the correct permissions:

```basic
# Set permissions for SSH directory
chmod 700 ~/.ssh

# Set permissions for private keys
chmod 600 ~/.ssh/id_rsa_account1
chmod 600 ~/.ssh/id_rsa_account2

# Set permissions for public keys
chmod 644 ~/.ssh/id_rsa_account1.pub
chmod 644 ~/.ssh/id_rsa_account2.pub
```

These permissions ensure:

* **700 for ~/.ssh**: Only you can read, write, and execute the directory
    
* **600 for private keys**: Only you can read and write your private keys
    
* **644 for public keys**: Only you can write, but everyone can read
    

## 7\. Configure Git User Identity Per Repository

When working with multiple accounts, you may want to configure your Git user identity per repository to ensure commits are attributed to the correct account:

```ruby
# Navigate to your repository
cd /path/to/repository

# Set user name for this repository
git config user.name "Your Name"

# Set user email for this repository
git config user.email "your-email@example.com"

# Verify the configuration
git config --list
```

If you want to set this globally for all repositories, use the `--global` flag:

```ruby
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 7.1 Important: Fixing Commits with Wrong Account

If you notice that your commits are still being attributed to your old/work account instead of the correct one, you need to fix the repository configuration:

```ruby
# Navigate to your repository
cd /path/to/repository

# Set the correct user email for this repository
git config user.email "your_email@example.com"

# Verify the configuration was updated
git config user.email
```

Make sure to:

1. Use the **correct email address** for your intended account
    
2. Run this command **inside the repository directory** (not globally)
    
3. Verify the output shows your intended email address
    
4. Test with a new commit to ensure it's attributed correctly
    

If commits were already made with the wrong account, you'll need to rewrite the commit history to fix the author information. This is beyond the scope of this guide, but tools like `git filter-repo` or `git filter-branch` can help.8. Verify SSH Connection

Before cloning or pushing to a repository, verify that your SSH connection is working correctly:

```ruby
# Test connection to GitHub with account1
ssh -T git@github.com-account1

# Test connection to GitHub with account2
ssh -T git@github.com-account2
```

You should see a response like:

```ruby
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

If you encounter any issues, use the verbose flag to debug:

```ruby
ssh -vT git@github.com-account1
```

## Troubleshooting Common Issues

### Issue 1: Permission Denied (publickey)

**Problem**: You get "Permission denied (publickey)" error when trying to push or pull.

**Solution**:

1. Verify your SSH key is added to the GitHub account
    
2. Check that the SSH key file has correct permissions (chmod 600)
    
3. Ensure you're using the correct hostname (e.g., [`git@github.com`](mailto:git@github.com)`-account1`)
    
4. Test the connection: `ssh -T` [`git@github.com`](mailto:git@github.com)`-account1`
    

### Issue 2: Using Wrong Account

**Problem**: Git is using the wrong account for push/pull operations.

**Solution**:

1. Verify the remote URL with `git remote -v`
    
2. Ensure the hostname matches your SSH config (e.g., [`github.com`](http://github.com)`-account1` not [`github.com`](http://github.com))
    
3. Check git config: `git config --local` [`user.email`](http://user.email)
    
4. Update remote if needed: `git remote set-url origin` [`git@github.com`](mailto:git@github.com)`-account1:username/repo.git`
    

### Issue 3: SSH Key Not Found

**Problem**: "Could not open a connection to your authentication agent" or SSH key not found.

**Solution**:

1. Start SSH agent: `eval "$(ssh-agent -s)"`
    
2. Add your SSH key: `ssh-add ~/.ssh/id_rsa_account1`
    
3. Verify key is added: `ssh-add -l`
    

### Issue 4: Multiple SSH Keys in Agent

**Problem**: SSH agent tries wrong key first, causing "too many authentication failures".

**Solution**: Modify your ~/.ssh/config to specify which key to use first:

```ruby
Host github.com-account1
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa_account1
  IdentitiesOnly yes

Host github.com-account2
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa_account2
  IdentitiesOnly yes
```

The `IdentitiesOnly yes` option ensures only the specified key is used.

## Best Practices and Tips

1. **Use Descriptive Hostnames**: Make your SSH config hostnames descriptive (e.g., [`github.com`](http://github.com)`-work`, [`github.com`](http://github.com)`-personal`)
    
2. **Keep Keys Secure**: Never share your private SSH keys and consider using a passphrase for added security
    
3. **Regularly Rotate Keys**: Periodically generate new SSH keys for security
    
4. **Use SSH Agent**: Add your keys to SSH agent for seamless authentication:
    
    ```ruby
    ssh-add ~/.ssh/id_rsa_account1
    ssh-add ~/.ssh/id_rsa_account2
    ```
    
5. **Document Your Setup**: Keep a record of which key belongs to which account
    
6. **Test Before Critical Operations**: Always test SSH connection before important push/pull operations
    
7. **Monitor SSH Activity**: Regularly check active SSH keys on your GitHub accounts (Settings &gt; SSH and GPG keys)
    

## Conclusion

Managing multiple GitHub accounts on the same machine is a common workflow for developers who maintain both personal and work projects. By following these steps, you can:

* Generate and manage multiple SSH keys securely
    
* Configure SSH to use different keys for different accounts
    
* Associate repositories with the correct GitHub accounts
    
* Debug and troubleshoot common authentication issues
    

The key to success is ensuring that:

* SSH keys have correct permissions
    
* SSH config maps hostnames to the right keys
    
* Git remotes use the correct custom hostnames
    
* Each repository is configured with the right user identity
    

With this setup, you can seamlessly switch between multiple GitHub accounts without authentication headaches. Remember to keep your SSH keys secure and regularly review your active keys on GitHub's settings page.remote origin URL for each GitHub account.