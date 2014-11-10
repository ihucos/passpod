### What is Passpod?

Passpod is a library that hashes and saves passwords in a safe way.
Although already usable it is still a prototype. Feedback very welcome.

**How currently web platforms save passwords**

| User           | Password Hash |
| -------------- | ------------- |
| BieberLover93  | 356a192b79... |
| EnterpriseUser | da4b9237ba... |
| iorfsjadk      | 77de68daec... |
|      ...       |      ...      |

**How Passpod saves passwords**

| Hash           |
| -------------- |
| 1b645389247... |
| ac3478d69a3... |
| c1dfd96eea8... |
| 902ba3cda18... |
|      ...       |

The idea is to minimize the harm that a compromised password database can cause.
A leaked Passpod database does not contain a direct link between a user name and its hashed password, this makes brute force attacks more expensive.
When sufficient dummy hash entries are created, it is difficult to get the approximate number of registered users.

The design of Passpod also encourages the use of a separate Database for password storage,
preventing SQL injections attacks targeting the application to compromise the hashed passwords.
Often password hashing is implemented on the fly and bundled with application code,
Passpod hopes to offer an modularized, better reviewed, more secure alternative.

### How To Use It

Passpod offers a Python library with a simple dictionary-like interface.
```python
>>> from passpod impor passpod
>>> passwords = passpod.open('sqlite:///tmp/mydb') # passwords is a dictionary-like object
>>> psswords['user1'] = 'mypassword$*!'
>>> 'user1' in passwords
True
>>> passwords['user1'] == 'mypassword$*!'
True
>>> del passwords['user1']
```
