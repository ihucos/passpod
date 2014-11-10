### What is Passpod?

Passpod is a library that hashes and saves passwords in a safe way.
Altough already usable it is thought as a prototype to test a new way to save passwords Feedback wellcomme.

How currently web platforms save passwords

| User           | Password Hash |
| -------------- | ------------- |
| BieberLover93  | 356a192b79... |
| EnterpriseUser | da4b9237ba... |
| iorfsjadk      | 77de68daec... |
|      ...       |      ...      |

How Passpod saves passwords:

| Hash           |
| -------------- |
| 1b645389247... |
| ac3478d69a3... |
| c1dfd96eea8... |
| 902ba3cda18... |
|      ...       |

The idea is to minimize the harm that compromissed passwords hashes can cause.
An leaked passpod database does not contain a direct link between a username and its hashed password, this makes brute force attacks more difficult.
When sufficient dummy hash entries are created, its not possible to get an approximate number of registered users.

The design of Passpod also encourages the use of a separate Database for password storage,
preventing application SQL injections attaks to compromisse the hashed passwords.
Often password hashing is implemented on the fly and bundled with application code,
passpod hopes to offer an modularized, better reviewed, more secure alternative.

### How To Use It

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
